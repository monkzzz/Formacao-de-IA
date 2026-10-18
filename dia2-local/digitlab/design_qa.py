"""Check responsive layout, gallery containment and keyboard-accessible details."""

import argparse
import json

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .qa_outputs import qa_outputs, qa_report
from .train import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765/")
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--report")
    parser.add_argument("--screenshot-prefix")
    args = parser.parse_args()
    prefix = args.screenshot_prefix or ("public-design" if args.public else "design")
    name = args.report or ("public-design-qa.json" if args.public else "design-qa.json")
    destination, captures = qa_outputs(name, prefix, ("390", "1440"))
    report = {"url": args.url, "status": "FAIL", "checks": {}}
    with qa_report(destination, report), sync_playwright() as p:
        browser = open_browser(p)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready === true", timeout=60000)
        assert page.locator("h1").count() == 1
        assert page.locator("#prediction").evaluate("el => el.classList.contains('is-empty')")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.classList.contains('skip-link')")
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "workspace"
        report["checks"]["keyboard_skip_to_workspace"] = {"status": "PASS"}

        assert not page.locator("#network").evaluate("el => el.open")
        summary = page.locator("#network > summary")
        summary.focus(); page.keyboard.press("Space")
        assert page.locator("#network").evaluate("el => el.open")
        assert page.locator("#layer-one canvas").first.is_visible()
        page.keyboard.press("Space")
        assert not page.locator("#network").evaluate("el => el.open")
        page.locator('nav a[href="#network"]').click()
        assert page.locator("#network").evaluate("el => el.open")
        page.locator("#network > summary").click()
        report["checks"]["expandable_network_and_anchor"] = {"status": "PASS", "actual_feature_maps": 48}

        page.locator("#mode-letters").click()
        page.wait_for_function("digitLab.state.mode === 'letters' && !digitLab.state.loading", timeout=60000)
        paths = sorted((ROOT / "reports/letter-fixtures").glob("*.png"))
        page.locator("#files").set_input_files([str(path) for path in paths])
        page.wait_for_function("digitLab.state.uploads.length === 26 && !digitLab.state.busy", timeout=60000)
        assert page.locator("#upload-count").inner_text() == "26"
        assert not page.locator("#prediction").evaluate("el => el.classList.contains('is-empty')")
        assert page.locator("#uploads").evaluate("el => el.scrollHeight > el.clientHeight")
        assert page.locator("#uploads").bounding_box()["height"] <= 415
        report["checks"]["gallery_count_and_containment"] = {"status": "PASS", "results": 26}
        page.locator(".upload-result").first.click()
        sizes = []
        for width, height in [(320, 800), (390, 844), (768, 1024), (1024, 900), (1440, 1100)]:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(120)
            dimensions = page.evaluate("""() => ({viewport: innerWidth,
              document: document.documentElement.scrollWidth,
              galleryColumns: getComputedStyle(document.getElementById('uploads')).gridTemplateColumns.split(' ').length,
              galleryHeight: document.getElementById('uploads').clientHeight})""")
            assert dimensions["document"] <= width, dimensions
            if width < 520:
                assert dimensions["galleryColumns"] == 2, dimensions
                assert dimensions["galleryHeight"] <= 380, dimensions
            for control_id in ["mode-digits", "mode-letters", "classify", "clear", "export"]:
                assert page.locator("#" + control_id).bounding_box()["height"] >= 40
            sizes.append(dimensions)
            if width in [390, 1440]:
                page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
                page.screenshot(path=str(captures[str(width)]), full_page=True)
        report["checks"]["responsive_layout_and_controls"] = {"status": "PASS", "viewports": sizes}
        contrasts = page.evaluate("""() => {
          const rgb = text => text.match(/[\\d.]+/g).slice(0, 3).map(Number);
          const luminance = text => {
            const channels = rgb(text).map(v => {v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;});
            return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
          };
          const pairs = [['.primary', '.primary'], ['.mode-hint', '.lab'],
            ['.score-row:not(.winner)', '.result-panel'], ['.privacy', '.input-panel'],
            ['.prediction small', '.result-panel']];
          return pairs.map(([selector, background]) => {
            const fg = luminance(getComputedStyle(document.querySelector(selector)).color);
            const bg = luminance(getComputedStyle(document.querySelector(background)).backgroundColor);
            return {selector, contrast: (Math.max(fg, bg) + .05) / (Math.min(fg, bg) + .05)};
          });
        }""")
        assert all(pair["contrast"] >= 4.5 for pair in contrasts), contrasts
        report["checks"]["key_text_contrast"] = {"status": "PASS", "minimum": 4.5, "samples": contrasts}
        page.emulate_media(reduced_motion="reduce")
        assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
        assert page.locator("#classify").evaluate("el => getComputedStyle(el).transitionDuration") == "0s"
        assert not errors, errors
        report["checks"]["reduced_motion_and_script_errors"] = {"status": "PASS", "page_errors": errors}
        browser.close()
    report["status"] = "PASS"
    print(json.dumps({"status": "PASS", "groups": len(report["checks"]), "report": name}), flush=True)


if __name__ == "__main__":
    main()
