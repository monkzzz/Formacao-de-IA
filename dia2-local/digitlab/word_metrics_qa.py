"""Check published word percentages against the frozen larger evaluation."""

import argparse
import hashlib
import json
import re

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8770/")
    parser.add_argument("--report", required=True)
    parser.add_argument("--screenshot-prefix", default="word-metrics")
    args = parser.parse_args()
    destination = ROOT / "reports" / args.report
    if destination.exists():
        raise SystemExit("Refusing to overwrite existing evidence")
    measured = json.loads((ROOT / "reports/words-1000-evaluation.json").read_text(encoding="utf-8"))
    protocol = json.loads((ROOT / "reports/words-1000-protocol.json").read_text(encoding="utf-8"))
    assert measured["status"] == "PASS" and measured["lines"] == 1000
    assert abs(measured["word_accuracy"] - (1 - measured["word_edits"] / measured["reference_words"])) < 1e-12
    for path, expected in protocol["source_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    report = {"url": args.url, "status": "FAIL", "evaluation": "words-1000-evaluation.json", "checks": {}}
    checks = report["checks"]
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append((request.method, request.url)))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        assert page.locator(".benchmark").count() == 3
        for mode in ("digits", "letters"):
            manifest = json.loads((ROOT / "dist/model/robust" / mode / "manifest.json").read_text())
            expected = f"{manifest['training']['test']['accuracy'] * 100:.2f}"
            assert expected in page.locator("#benchmark-" + mode).inner_text()
        expected = f"{measured['word_accuracy'] * 100:.2f}"
        assert expected in page.locator("#word-accuracy").inner_text()
        assert "1,000" in page.locator("#benchmark-words").inner_text()
        assert "Full precision" in page.locator("#benchmark-words").inner_text()
        checks["three_measured_scores_match_sources"] = {"status": "PASS", "word_accuracy_percent": expected}
        details = page.locator("#word-benchmark-details")
        summary = details.locator("summary")
        assert not details.evaluate("el => el.open")
        summary.focus(); page.keyboard.press("Enter")
        assert details.evaluate("el => el.open")
        body = details.inner_text()
        for value in (f"{measured['reference_words']:,}", f"{measured['word_error_rate'] * 100:.2f}%",
                      f"{measured['character_error_rate'] * 100:.2f}%", f"{measured['exact_line_accuracy'] * 100:.2f}%"):
            assert value in body, value
        assert "1" in body and "word error rate" in body
        page.keyboard.press("Space")
        assert not details.evaluate("el => el.open")
        checks["keyboard_details_show_rates_counts_and_definition"] = {"status": "PASS"}
        page.locator("#helper-launcher").click()
        page.locator("#helper-question").fill("What is the word recognition accuracy?")
        page.locator("#helper-question").press("Enter")
        answer = page.locator(".helper-message").last
        assert expected in answer.inner_text()
        answer.get_by_role("button", name="See word test details").click()
        assert details.evaluate("el => el.open")
        assert page.locator("#scopedog").is_hidden()
        checks["helper_uses_displayed_metrics_and_opens_details"] = {"status": "PASS"}
        page.locator("#mode-letters").click()
        page.wait_for_function("digitLab.state.mode === 'letters' && digitLab.state.ready")
        page.locator("#mode-words").click()
        assert page.locator("#words-workspace").is_visible()
        assert page.locator("#word-quality").input_value() == "precise"
        page.locator("#word-quality").select_option("standard")
        assert "Full precision" in page.locator("#benchmark-words").inner_text()
        assert page.locator("#word-eraser").is_enabled()
        checks["mode_switches_preserve_score_scope_and_controls"] = {"status": "PASS"}
        for width, height in ((1440, 1100), (390, 844), (320, 740), (844, 390)):
            page.set_viewport_size({"width": width, "height": height})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), width
            box = page.locator("#benchmark-words").bounding_box()
            assert box["x"] >= 0 and box["x"] + box["width"] <= width
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        page.locator("#mode-digits").click()
        page.wait_for_function("digitLab.state.ready")
        details.evaluate("el => {el.open=false;}")
        page.evaluate("() => {document.activeElement.blur();scrollTo(0,0);}")
        page.set_viewport_size({"width": 1440, "height": 1100})
        page.screenshot(path=str(screenshots / (args.screenshot_prefix + "-desktop.png")), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(screenshots / (args.screenshot_prefix + "-mobile.png")), full_page=True)
        checks["desktop_mobile_and_landscape_layouts"] = {"status": "PASS"}
        assert not errors, errors
        assert not any("huggingface.co" in url or "jsdelivr.net" in url for _, url in requests)
        assert all(method == "GET" for method, _ in requests)
        checks["no_model_prefetch_uploads_or_script_errors"] = {"status": "PASS"}
        version = page.locator("#app-version").inner_text().removeprefix("v")
        assert page.evaluate("digitLab.exportRecord().application_version") == version
        report["application_version"] = version
        checks["release_version_matches_exports"] = {"status": "PASS"}
        public = page.request.get(args.url.rstrip("/") + "/evaluation/words-1000.json")
        assert public.ok
        summary = public.json()
        assert summary["lines"] == measured["lines"]
        assert summary["reference_words"] == measured["reference_words"]
        assert summary["word_accuracy"] == measured["word_accuracy"]
        checks["downloadable_summary_matches_evaluation"] = {"status": "PASS"}
        browser.close()
    report["status"] = "PASS"
    write_json(destination, report)
    print(json.dumps({"status": "PASS", "groups": len(checks), "report": args.report}))


if __name__ == "__main__":
    main()
