"""Supplement existing parity QA with public drawing and release identity checks."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dia2-local"))
from playwright.sync_api import sync_playwright
from digitlab.qa import open_browser
from digitlab.words_qa import check_drawing_tools


def main():
    destination = Path(__file__).with_name("submission-public-interactions.json")
    if destination.exists():
        raise SystemExit("Evidence exists; choose a new destination before rerunning")
    url = "https://naoquerosaber.pt/AI/"
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "url": url,
              "status": "FAIL", "checks": {}, "limits": [
                  "Automated Edge mouse and emulated touch; no physical touchscreen test",
                  "No official challenge inputs, training or optional reader inference",
                  "Existing host retained; GitHub Pages and instructor acceptance pending"]}
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            context = browser.new_context(viewport={"width": 1440, "height": 1100}, has_touch=True)
            page = context.new_page()
            page.goto(url)
            page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
            report["release"] = page.locator("#app-version").inner_text()
            report["model_sha256"] = page.evaluate("digitLab.state.model.manifest.sha256")
            options = page.locator("#digit-reader").inner_text()
            assert page.locator("#digit-reader").input_value() == "local"
            assert "trained here" in options and "default" in options
            about = page.locator("#digit-reader-about").text_content()
            assert "pretrained" in about and "did not train these external weights" in about
            assert "pretrained" in page.locator("#word-about").text_content()
            report["checks"]["trained_default_and_pretrained_extensions"] = True
            check_drawing_tools(page, "drawing", "drawing", "clear")
            report["checks"]["mouse_eraser_undo_redo_clear"] = True
            canvas = page.locator("#drawing")
            blank = canvas.evaluate("c => c.toDataURL()")
            canvas.scroll_into_view_if_needed()
            box = canvas.bounding_box()
            session = context.new_cdp_session(page)
            x, y = box["x"] + box["width"] * .3, box["y"] + box["height"] * .3
            for event, points in [("touchStart", [{"x": x, "y": y}]),
                                  ("touchMove", [{"x": x + 35, "y": y + 70}]),
                                  ("touchEnd", [])]:
                session.send("Input.dispatchTouchEvent", {"type": event, "touchPoints": points})
            assert canvas.evaluate("c => c.toDataURL()") != blank
            page.locator("#classify").click()
            page.wait_for_function("!digitLab.state.busy && !document.querySelector('#prediction').classList.contains('is-empty')")
            assert page.locator("#layer-one canvas").count() == 16
            page.locator("#clear").click()
            assert canvas.evaluate("c => c.toDataURL()") == blank
            assert "is-empty" in page.locator("#prediction").get_attribute("class")
            report["checks"]["emulated_touch_classify_clear"] = True
            fixture = ROOT / "dia2-local/reports/mnist-fixtures/0.png"
            if not fixture.exists():
                fixture = next((ROOT / "dia2-local/reports/mnist-fixtures").glob("*.png"))
            page.locator("#files").set_input_files(str(fixture))
            page.wait_for_function("digitLab.state.uploads.length === 1 && !digitLab.state.busy")
            prediction = page.evaluate("digitLab.exportRecord().predictions[0]")
            assert "error" not in prediction and len(prediction["scores"]) == 10
            report["checks"]["individual_upload"] = {"file": fixture.name, "model_sha256": prediction["model_sha256"]}
            screenshot = ROOT / "dia2-local/reports/screenshots/submission-20261017-desktop.png"
            page.screenshot(path=str(screenshot), full_page=True)
            report["screenshot"] = str(screenshot.relative_to(ROOT)).replace("\\", "/")
            browser.close()
        identities = []
        for relative in ["index.html", "v3/app.js",
                         "model/captcha-v3/digits/manifest.json", "model/captcha-v3/digits/weights.bin",
                         "model/robust/letters/weights.bin"]:
            local = ROOT / "dia2-local/dist" / relative
            with urlopen(url + relative, timeout=60) as response:
                remote = response.read()
            digest = hashlib.sha256(remote).hexdigest()
            assert digest == hashlib.sha256(local.read_bytes()).hexdigest(), relative
            identities.append({"path": relative, "sha256": digest, "bytes": len(remote)})
        report["checks"]["public_asset_identity"] = identities
        report["status"] = "PASS"
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
