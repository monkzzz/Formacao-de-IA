"""Separate Words UI checks, CNN parity checks, and optional real TrOCR smoke test."""

import argparse
import io
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


STUB_WORKER = """
self.onmessage = ({data}) => {
  self.postMessage({id:data.id, type:'progress', message:'Test worker is reading…'});
  setTimeout(() => self.postMessage({id:data.id, type:'result',
    text:'<b>Hello</b>', elapsed:12, model:'test-double', revision:'test-only'}), 100);
};
"""


def check_drawing_tools(page, canvas_id, prefix, clear_id, screenshot=None):
    page.locator("#" + clear_id).click()
    canvas = page.locator("#" + canvas_id)
    canvas.scroll_into_view_if_needed()
    blank = canvas.evaluate("c => c.toDataURL()")
    box = canvas.bounding_box()
    y = box["y"] + box["height"] * .5
    page.locator(f"#{prefix}-pen").click()
    page.mouse.move(box["x"] + box["width"] * .2, y)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] * .8, y, steps=12)
    page.mouse.up()
    drawn = canvas.evaluate("c => c.toDataURL()")
    assert drawn != blank
    page.locator(f"#{prefix}-eraser").click()
    slider = page.locator(f"#{prefix}-eraser-size")
    assert slider.is_visible()
    slider.evaluate("el => {el.value='60';el.dispatchEvent(new Event('input',{bubbles:true}));}")
    assert page.locator(f"#{prefix}-eraser").get_attribute("aria-pressed") == "true"
    box = canvas.bounding_box(); y = box["y"] + box["height"] * .5
    page.mouse.click(box["x"] + box["width"] * .5, y)
    erased = canvas.evaluate("c => c.toDataURL()")
    assert erased != drawn and erased != blank
    assert canvas.evaluate("c => getComputedStyle(c).cursor.includes('data:image/svg+xml')")
    if screenshot:
        screenshot.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True)
    page.locator(f"#{prefix}-undo").click()
    assert canvas.evaluate("c => c.toDataURL()") == drawn
    page.locator(f"#{prefix}-redo").click()
    assert canvas.evaluate("c => c.toDataURL()") == erased
    canvas.focus()
    page.keyboard.press("Control+z")
    assert canvas.evaluate("c => c.toDataURL()") == drawn
    page.keyboard.press("Control+Shift+z")
    assert canvas.evaluate("c => c.toDataURL()") == erased
    page.locator("#" + clear_id).click()
    assert canvas.evaluate("c => c.toDataURL()") == blank
    page.locator(f"#{prefix}-undo").click()
    assert canvas.evaluate("c => c.toDataURL()") == erased
    page.locator(f"#{prefix}-pen").click()
    box = canvas.bounding_box(); y = box["y"] + box["height"] * .5
    page.mouse.click(box["x"] + box["width"] * .3, y)
    assert page.locator(f"#{prefix}-redo").is_disabled()
    page.locator("#" + clear_id).click()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8770/")
    parser.add_argument("--live-image", type=Path,
                        help="Run actual browser TrOCR on this non-challenge handwriting image")
    parser.add_argument("--expected-text", help="Optional exact expected live transcription")
    parser.add_argument("--quality", choices=["standard", "precise"], default="precise")
    parser.add_argument("--report", default="words-browser-qa.json")
    parser.add_argument("--screenshot-prefix", default="words")
    args = parser.parse_args()
    report_path = ROOT / "reports" / args.report
    if report_path.exists():
        raise SystemExit(f"Refusing to overwrite existing evidence: {report_path}")
    checks = {}
    report = {"url": args.url, "status": "FAIL", "checks": checks}
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        context = browser.new_context(viewport={"width": 1440, "height": 1100},
                                      permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append((request.method, request.url)))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        version = page.locator("#app-version").inner_text().removeprefix("v")
        assert version == page.evaluate("digitLab.applicationVersion")
        assert version == page.evaluate("digitLab.exportRecord().application_version")
        checks["visible_and_exported_release_version"] = {"status": "PASS", "version": version}
        report["application_version"] = version
        check_drawing_tools(page, "drawing", "drawing", "clear",
                            ROOT / "reports/screenshots" / (args.screenshot_prefix + "-character-eraser.png"))
        checks["character_eraser_size_undo_redo_and_keyboard"] = {"status": "PASS"}
        for mode in ("digits", "letters"):
            page.evaluate("mode => digitLab.activateMode(mode)", mode)
            fixture = json.loads((ROOT / "dist/model/robust" / mode / "parity.json").read_text())
            parity = page.evaluate("""fixture => fixture.cases.map(item => {
              const result = digitLab.predict(item.input);
              const delta = (a,b) => Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));
              return {logits:delta(result.logits,item.logits), hidden:delta(result.hidden,item.hidden),
                pool1:delta(result.first,item.pool1), pool2:delta(result.second,item.pool2)};
            })""", fixture)
            assert all(value <= .0001 for case in parity for value in case.values()), parity
            checks[mode + "_activation_parity"] = {"status": "PASS", "cases": parity}
        page.locator("#mode-words").click()
        assert page.locator("#word-quality").input_value() == "precise"
        checks["full_precision_is_default"] = {"status": "PASS"}
        assert page.locator("#words-workspace").is_visible()
        assert page.locator("#character-workspace").is_hidden()
        assert page.locator("#network").is_hidden()
        assert page.locator("#mode-words").get_attribute("aria-pressed") == "true"
        page.locator("#word-read").click()
        assert "non-blank" in page.locator("#word-status").inner_text()
        assert not any("huggingface.co" in url or "jsdelivr.net" in url for _, url in requests)
        checks["lazy_loading_and_blank_rejection"] = {"status": "PASS"}
        check_drawing_tools(page, "word-drawing", "word", "word-clear",
                            ROOT / "reports/screenshots" / (args.screenshot_prefix + "-word-eraser.png"))
        checks["word_eraser_size_undo_redo_and_keyboard"] = {"status": "PASS"}
        preparation = page.evaluate("""async () => {
          const {prepareWord} = await import('./v3/words.js?v=words-1');
          const inputs = [false,true].map(dark => {
            const c=document.createElement('canvas');c.width=120;c.height=50;
            const x=c.getContext('2d');x.fillStyle=dark?'black':'white';x.fillRect(0,0,120,50);
            x.fillStyle=dark?'white':'black';x.fillRect(20,10,20,30);x.fillRect(60,10,15,30);
            const out=prepareWord(c);
            return {width:out.width,height:out.height,pixels:Array.from(out.getContext('2d').getImageData(0,0,out.width,out.height).data)};
          });
          return {same:JSON.stringify(inputs[0])===JSON.stringify(inputs[1]),width:inputs[0].width,height:inputs[0].height};
        }""")
        assert preparation["same"] and preparation["width"] > preparation["height"]
        checks["word_preparation_polarity_and_shape"] = {"status": "PASS", **preparation}

        # Exercise UI plumbing with a clearly identified worker double, not an accuracy test.
        page.route("**/words-worker.js*", lambda route: route.fulfill(
            status=200, content_type="text/javascript", body=STUB_WORKER))
        page.evaluate("""() => {
          const c=document.getElementById('word-drawing'), ctx=c.getContext('2d');
          ctx.fillStyle='black'; ctx.font='100px cursive'; ctx.fillText('Hello',70,190);
        }""")
        page.locator("#word-read").click()
        page.wait_for_function("!digitLab.wordsContext().busy")
        assert page.locator("#word-text").input_value() == "<b>Hello</b>"
        assert page.locator("#word-raw").text_content() == "<b>Hello</b>"
        assert page.locator("#word-raw b").count() == 0
        assert page.locator("#word-preview").is_visible()
        page.locator("#word-text").fill("Hello corrected")
        assert page.locator("#word-raw").text_content() == "<b>Hello</b>"
        page.locator("#word-copy").click()
        page.wait_for_function("document.getElementById('word-status').textContent.includes('copied')")
        assert page.evaluate("navigator.clipboard.readText()") == "Hello corrected"
        with page.expect_download() as download:
            page.locator("#word-download").click()
        assert Path(download.value.path()).read_text(encoding="utf-8") == "Hello corrected"
        checks["editing_copy_download_and_safe_rendering"] = {"status": "PASS", "worker": "test-double"}
        page.locator("#word-quality").select_option("precise")
        assert page.locator("#word-text").input_value() == ""
        checks["quality_switch_clears_stale_transcription"] = {"status": "PASS"}
        drawing = page.locator("#word-drawing")
        drawing.scroll_into_view_if_needed()
        box = drawing.bounding_box()
        page.mouse.move(box["x"] + 30, box["y"] + 30)
        page.mouse.down()
        page.mouse.move(box["x"] + 80, box["y"] + 50, steps=10)
        page.mouse.up()
        assert page.locator("#word-text").input_value() == ""
        assert page.locator("#word-preview").is_hidden()
        checks["pointer_drawing_clears_stale_transcription"] = {"status": "PASS"}

        page.locator("#word-read").click()
        page.locator("#word-cancel").click()
        page.wait_for_function("!digitLab.wordsContext().busy")
        assert "cancelled" in page.locator("#word-status").inner_text()
        page.locator("#word-read").click()
        page.locator("#mode-digits").click()
        page.wait_for_function("digitLab.state.mode === 'digits' && !digitLab.wordsContext().busy")
        assert page.locator("#character-workspace").is_visible()
        page.locator("#mode-words").click()
        page.locator("#word-read").click()
        page.wait_for_function("!digitLab.wordsContext().busy")
        assert page.locator("#word-text").input_value() == "<b>Hello</b>"
        checks["cancel_switch_and_retry"] = {"status": "PASS", "worker": "test-double"}

        for name, content in (("broken.png", b"broken"), ("blank.png", None)):
            if content is None:
                buffer = io.BytesIO()
                Image.new("RGB", (100, 40), "white").save(buffer, format="PNG")
                content = buffer.getvalue()
            page.locator("#word-file").set_input_files({"name": name, "mimeType": "image/png", "buffer": content})
            page.wait_for_function("!digitLab.wordsContext().busy")
            assert page.locator("#word-status").evaluate("el => el.classList.contains('error')")
            assert page.locator("#word-text").input_value() == ""
        checks["invalid_and_blank_uploads"] = {"status": "PASS"}

        for width, height in ((1440, 1100), (390, 844), (320, 740), (844, 390)):
            page.set_viewport_size({"width": width, "height": height})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), width
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#word-text").focus()
        assert page.evaluate("document.activeElement.id") == "word-text"
        page.locator("#word-text").fill("A word")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "word-copy"
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshots / (args.screenshot_prefix + "-mobile.png")), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 1100})
        page.screenshot(path=str(screenshots / (args.screenshot_prefix + "-desktop.png")), full_page=True)
        checks["responsive_layout_and_keyboard"] = {"status": "PASS"}

        # A fresh page must recover after a worker/module load fails.
        failure = context.new_page()
        failure.route("**/words-worker.js*", lambda route: route.abort())
        failure.goto(args.url)
        failure.wait_for_function("window.digitLab?.state.ready")
        failure.locator("#mode-words").click()
        failure.evaluate("""() => {const x=document.getElementById('word-drawing').getContext('2d');
          x.fillStyle='black';x.fillRect(30,30,100,50);}""")
        failure.locator("#word-read").click()
        failure.wait_for_function("!digitLab.wordsContext().busy", timeout=30000)
        assert failure.locator("#word-status").evaluate("el => el.classList.contains('error')")
        failure.locator("#mode-letters").click()
        failure.wait_for_function("digitLab.state.mode === 'letters' && digitLab.state.ready")
        failure.close()
        checks["failed_worker_preserves_character_modes"] = {"status": "PASS"}
        helper = page.evaluate("""async () => {
          const {answerQuestion} = await import('./v3/helper-knowledge.js?v=words-1');
          return {words:answerQuestion('Can I write words?'),
            result:answerQuestion('Explain this prediction',{mode:'words',predicted:'Hello'})};
        }""")
        assert helper["words"]["topic"] == "words"
        assert helper["result"]["topic"] == "word-result"
        assert "Hello" in helper["result"]["text"]
        checks["helper_word_guidance_and_context"] = {"status": "PASS"}

        if args.live_image:
            live = context.new_page()
            live.on("pageerror", lambda error: errors.append(str(error)))
            live.on("request", lambda request: requests.append((request.method, request.url)))
            live.goto(args.url)
            live.wait_for_function("window.digitLab?.state.ready")
            live.locator("#mode-words").click()
            live.locator("#word-quality").select_option(args.quality)
            live.locator("#word-file").set_input_files(str(args.live_image.resolve()))
            live.wait_for_function("digitLab.wordsContext().busy")
            assert live.locator("#word-eraser").is_disabled()
            assert live.locator("#word-quality").is_disabled()
            live.wait_for_function("!digitLab.wordsContext().busy", timeout=300000)
            text = live.locator("#word-text").input_value()
            assert text, live.locator("#word-status").inner_text()
            assert live.evaluate("digitLab.wordsContext().metadata.model") == "Xenova/trocr-small-handwritten"
            assert live.evaluate("digitLab.wordsContext().metadata.application_version") == version
            assert live.evaluate("digitLab.wordsContext().metadata.profile") == args.quality
            assert live.evaluate("digitLab.wordsContext().metadata.precision") == ("float32" if args.quality == "precise" else "int8")
            if args.expected_text:
                assert text == args.expected_text, text
            checks["real_trocr_smoke"] = {"status": "PASS", "text": text,
                "expected": args.expected_text, "metadata": live.evaluate("digitLab.wordsContext().metadata"),
                "note": "One fixture smoke test; not a word accuracy benchmark."}
            live.screenshot(path=str(screenshots / (args.screenshot_prefix + "-live-desktop.png")), full_page=True)
            alternate = "standard" if args.quality == "precise" else "precise"
            live.locator("#word-quality").select_option(alternate)
            live.locator("#word-read").click()
            live.wait_for_function("!digitLab.wordsContext().busy", timeout=300000)
            alternate_text = live.locator("#word-text").input_value()
            assert alternate_text
            assert live.evaluate("digitLab.wordsContext().metadata.profile") == alternate
            checks["real_alternate_quality_profile"] = {"status": "PASS", "profile": alternate,
                "text": alternate_text, "metadata": live.evaluate("digitLab.wordsContext().metadata")}
            live.close()
        else:
            checks["real_trocr_smoke"] = {"status": "NOT RUN"}
        assert not errors, errors
        assert all(method == "GET" for method, _ in requests), requests
        checks["no_image_upload_requests"] = {"status": "PASS", "methods": sorted(set(method for method, _ in requests))}
        checks["page_errors"] = {"status": "PASS", "errors": errors}
        browser.close()
    report["status"] = "PASS"
    write_json(report_path, report)
    print(json.dumps({"status": report["status"], "groups": len(checks), "report": str(report_path)}))


if __name__ == "__main__":
    main()
