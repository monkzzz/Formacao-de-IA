"""Verify the Scopedog guide and classification together in the real browser."""

import argparse
import hashlib
import json

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8766/")
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--report-prefix", help="Use a separate report and screenshot prefix for follow-up checks")
    args = parser.parse_args()
    name = args.report_prefix or ("public-helper" if args.public else "helper")
    report = {"url": args.url, "checks": {}}
    original = ROOT / "scopedog-asset.jpg"
    asset = ROOT / "dist/assets/scopedog.jpg"
    assert asset.is_file()
    if original.exists():
        assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(asset.read_bytes()).digest()
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append({"url": request.url, "method": request.method}))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        before = page.evaluate("digitLab.state.model.manifest.sha256")
        launcher = page.locator("#helper-launcher")
        launcher.wait_for(state="visible")
        assert launcher.get_attribute("aria-expanded") == "false"
        launcher.focus(); page.keyboard.press("Enter")
        assert page.locator("#helper-question").evaluate("el => el === document.activeElement")
        assert launcher.get_attribute("aria-expanded") == "true"
        assert page.locator("#helper-launcher img").evaluate("el => el.complete && el.naturalWidth > 0")
        report["checks"]["mascot_keyboard_open_and_input_focus"] = "PASS"

        cases = [["How does the network work?", "pipeline"], ["What is convolution?", "architecture"],
                 ["How can I upload a picture?", "upload"], ["What does confidence mean?", "scores"],
                 ["How is the model trained?", "training"], ["Tell me about MNIST", "datasets"],
                 ["Are my images sent to a server?", "privacy"], ["What about the Desafio?", "challenge"],
                 ["What is tomorrow's weather?", "fallback"]]
        results = page.evaluate("""async cases => {
            const {answerQuestion} = await import('./v3/helper-knowledge.js?v=scopedog-1');
            return cases.map(([question]) => answerQuestion(question).topic);
        }""", cases)
        assert results == [case[1] for case in cases], results
        report["checks"]["knowledge_routing_and_honest_fallback"] = {"status": "PASS", "cases": cases}

        def ask(text):
            page.locator("#helper-question").fill(text)
            page.locator("#helper-question").press("Enter")
            return page.locator(".helper-message").last.inner_text()

        assert "isn’t a prediction" in ask("Explain this prediction")
        assert "not calibrated" in ask("What does confidence mean?")
        assert "not a new blind test" in ask("Explain the Desafio")
        malicious = '<img src=x onerror="window.helperInjected=true">'
        ask(malicious)
        assert page.locator(".helper-message.is-user").last.inner_text().endswith(malicious)
        assert page.locator("#helper-messages img").count() == 0
        assert not page.evaluate("Boolean(window.helperInjected)")
        report["checks"]["typed_questions_context_and_safe_text_rendering"] = "PASS"

        page.keyboard.press("Escape")
        assert page.locator("#scopedog").is_hidden()
        assert launcher.evaluate("el => el === document.activeElement")
        page.locator("#files").set_input_files(str(ROOT / "reports/mnist-fixtures/digit-7.png"))
        page.wait_for_function("digitLab.state.uploads.length === 1 && !digitLab.state.busy")
        predicted = page.locator("#predicted").inner_text()
        launcher.click()
        assert f"shows {predicted} in digits mode" in ask("Explain this prediction")
        ask("What are feature maps?")
        page.locator(".helper-message").last.get_by_role("button", name="Explore the real feature maps").click()
        assert page.locator("#network").evaluate("el => el.open")
        assert page.locator("#network").evaluate("el => el === document.activeElement")
        assert page.locator("#scopedog").is_hidden()
        assert page.evaluate("digitLab.state.model.manifest.sha256") == before
        report["checks"]["prediction_context_navigation_and_model_unchanged"] = "PASS"

        launcher.click()
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshots / (name + "-desktop.png")), full_page=True)
        sizes = []
        for width, height in [(320, 568), (390, 844), (844, 390)]:
            page.set_viewport_size({"width": width, "height": height})
            box = page.locator("#scopedog").bounding_box()
            assert box["x"] >= 0 and box["y"] >= 0
            assert box["x"] + box["width"] <= width and box["y"] + box["height"] <= height
            assert page.locator("#helper-question").is_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            sizes.append([width, height])
            if width == 390:
                page.screenshot(path=str(screenshots / (name + "-mobile.png")), full_page=True)
        report["checks"]["mobile_portrait_and_landscape"] = {"status": "PASS", "viewports": sizes}
        page.emulate_media(reduced_motion="reduce")
        assert page.locator("#helper-messages").evaluate("el => getComputedStyle(el).scrollBehavior") == "auto"
        assert not errors, errors
        assert all(request["method"] == "GET" and (request["url"].startswith(args.url)
            or request["url"].startswith("blob:")) for request in requests)
        report["checks"]["no_chat_api_requests_or_script_errors"] = "PASS"
        browser.close()
    report["status"] = "PASS"
    write_json(ROOT / "reports" / (name + "-qa.json"), report)
    print(json.dumps({"status": "PASS", "groups": len(report["checks"]), "report": name + "-qa.json"}))


if __name__ == "__main__":
    main()
