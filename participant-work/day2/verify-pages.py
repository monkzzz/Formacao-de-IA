"""Verify public Pages assets, drawing and browser-only inference after deployment."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dia2-local"))
from playwright.sync_api import sync_playwright
from digitlab.qa import open_browser
from digitlab.words_qa import check_drawing_tools


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("Preserve prior evidence; select a new report")
    url = "https://monkzzz.github.io/Formacao-de-IA/"
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "url": url,
              "status": "FAIL", "checks": {}, "limits": [
                  "Automated Edge mouse and emulated touch, no physical touchscreen",
                  "Optional OCR and arcade ROM excluded from verification",
                  "No training or accuracy claim; separate frozen-challenge deployment comparison"]}
    try:
        with urlopen(url + "pages-build.json", timeout=60) as response:
            build = json.load(response)
        report["source_commit"] = build["source_commit"]
        assets = {}
        for name, expected in build["asset_sha256"].items():
            with urlopen(url + name, timeout=60) as response:
                actual = hashlib.sha256(response.read()).hexdigest()
                if name.endswith(".js"):
                    assert "javascript" in response.headers.get("Content-Type", ""), name
            assert actual == expected, name
            local = ROOT / "dia2-local/dist" / name
            if name.endswith("weights.bin"):
                assert hashlib.sha256(local.read_bytes()).hexdigest() == expected, name
            elif name != ".nojekyll":
                committed = subprocess.check_output(
                    ["rtk", "proxy", "git", "show", build["source_commit"] + ":dia2-local/dist/" + name], cwd=ROOT)
                assert hashlib.sha256(committed).hexdigest() == expected, name
            assets[name] = actual
        report["asset_sha256"] = assets
        report["checks"]["public_assets_and_javascript_mime"] = len(assets)
        # Read-only identity check of the existing site, which this workflow never writes.
        report["preserved_existing_origin"] = {}
        for name in ["index.html", "v3/app.js", "model/captcha-v3/digits/weights.bin"]:
            with urlopen("https://naoquerosaber.pt/AI/" + name, timeout=60) as response:
                actual = hashlib.sha256(response.read()).hexdigest()
            assert actual == hashlib.sha256((ROOT / "dia2-local/dist" / name).read_bytes()).hexdigest()
            report["preserved_existing_origin"][name] = actual
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            context = browser.new_context(viewport={"width": 1440, "height": 1100}, has_touch=True)
            page = context.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append({"method": request.method, "url": request.url}))
            page.goto(url)
            page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
            report["release"] = page.locator("#app-version").inner_text()
            report["model_sha256"] = page.evaluate("digitLab.state.model.manifest.sha256")
            assert report["model_sha256"] == assets["model/captcha-v3/digits/weights.bin"]
            assert page.locator("#digit-reader").input_value() == "local"
            check_drawing_tools(page, "drawing", "drawing", "clear")
            report["checks"]["mouse_eraser_undo_redo_clear"] = True
            canvas = page.locator("#drawing")
            blank = canvas.evaluate("c => c.toDataURL()")
            canvas.scroll_into_view_if_needed()
            box = canvas.bounding_box()
            session = context.new_cdp_session(page)
            x, y = box["x"] + box["width"] * .3, box["y"] + box["height"] * .3
            for event, points in [("touchStart", [{"x": x, "y": y}]),
                                  ("touchMove", [{"x": x + 35, "y": y + 70}]), ("touchEnd", [])]:
                session.send("Input.dispatchTouchEvent", {"type": event, "touchPoints": points})
            assert canvas.evaluate("c => c.toDataURL()") != blank
            page.locator("#classify").click()
            page.wait_for_function("!digitLab.state.busy && !document.querySelector('#prediction').classList.contains('is-empty')")
            assert page.locator("#layer-one canvas").count() == 16
            report["checks"]["emulated_touch_real_classification_and_layers"] = True
            screenshot = ROOT / "dia2-local/reports/screenshots/pages-20261017-desktop.png"
            page.screenshot(path=str(screenshot), full_page=True)
            report["screenshot"] = str(screenshot.relative_to(ROOT))
            page.locator("#clear").click()
            assert canvas.evaluate("c => c.toDataURL()") == blank
            assert "is-empty" in page.locator("#prediction").get_attribute("class")
            assert not errors, errors
            assert all(item["method"] == "GET" and (item["url"].startswith(url) or item["url"].startswith("blob:")) for item in requests)
            report["checks"]["browser_only_inference"] = True
            report["page_errors"] = errors
            report["requests"] = requests
            browser.close()
        report["status"] = "PASS"
    finally:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(assets)} live assets, preserved original site, drawing/touch and browser-only inference")


if __name__ == "__main__":
    main()
