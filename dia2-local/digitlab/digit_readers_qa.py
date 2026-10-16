"""Selectable digit OCR integration checks; optional real-model smoke tests, no challenge inputs."""

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


STUB = """
self.onmessage = ({data}) => {
  self.postMessage({id:data.id,type:'progress',message:'Test digit reader loading'});
  if(data.reader==='captcha-digits') {
    setTimeout(()=>self.postMessage({id:data.id,type:'result',text:'7',raw_text:'X',
      scores:Array.from({length:10},(_,i)=>i===7?.91:.01),elapsed:12}),300);
    return;
  }
  const text = data.reader === 'handwritten' ? '<b>7</b>' : data.profile === 'precise' ? 'O' : '7';
  setTimeout(() => self.postMessage({id:data.id,type:'result',text,elapsed:12}), 300);
};
"""


def fixture():
    image = Image.new("RGB", (160, 160), "white")
    draw = ImageDraw.Draw(image)
    draw.line([(45, 35), (115, 35), (65, 135)], fill="black", width=12)
    data = io.BytesIO()
    image.save(data, format="PNG")
    return {"name": "synthetic-seven.png", "mimeType": "image/png", "buffer": data.getvalue()}


def wait_idle(page):
    page.wait_for_function("!digitLab.state.busy && !digitLab.state.loading")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8782/")
    parser.add_argument("--report", required=True)
    parser.add_argument("--live", action="store_true", help="Download and execute both actual Standard OCR models")
    args = parser.parse_args()
    destination = ROOT / "reports" / args.report
    if destination.exists():
        raise SystemExit("Refusing to overwrite existing evidence")
    checks = {}
    report = {"status": "FAIL", "checks": checks, "live": "NOT RUN", "captcha_accuracy": "NOT RUN"}
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append((request.method, request.url)))
        page.route("**/digit-reader-worker.js*", lambda route: route.fulfill(body=STUB, content_type="text/javascript"))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready")
        assert page.locator("#digit-reader").input_value() == "local"
        assert page.locator("#network").is_visible()
        for mode in ("digits", "letters"):
            page.evaluate("mode => digitLab.activateMode(mode)", mode)
            experiment = "captcha-v3" if mode == "digits" else "robust"
            parity = json.loads((ROOT / "dist/model" / experiment / mode / "parity.json").read_text())
            delta = page.evaluate("""fixture => Math.max(...fixture.cases.map(item => {
              const out = digitLab.predict(item.input);
              return ['logits','hidden'].flatMap(k => Array.from(out[k],(v,i)=>Math.abs(v-item[k][i])))
                .concat(Array.from(out.first,(v,i)=>Math.abs(v-item.pool1[i])),Array.from(out.second,(v,i)=>Math.abs(v-item.pool2[i])))
                .reduce((maximum,v)=>Math.max(maximum,v),0);
            }))""", parity)
            assert delta <= .0001, delta
            checks[mode + "_unchanged_activation_parity"] = {"status": "PASS", "max_delta": delta}
        page.locator("#mode-digits").click()
        page.locator("#digit-reader").select_option("printed")
        assert page.locator("#network").is_hidden() and page.locator("#model").is_hidden()
        assert page.locator("#scores").is_hidden()
        page.locator("#classify").click()
        wait_idle(page)
        assert "non-blank" in page.locator("#status").inner_text()
        assert not any("huggingface.co" in url or "jsdelivr.net" in url for _, url in requests)
        checks["lazy_download_blank_rejection_and_honest_views"] = "PASS"
        page.locator("#drawing").evaluate("""c => {
          const x=c.getContext('2d');x.strokeStyle='white';x.lineWidth=20;
          x.beginPath();x.moveTo(60,50);x.lineTo(210,50);x.lineTo(100,220);x.stroke();
        }""")
        page.locator("#classify").click()
        wait_idle(page)
        assert page.locator("#predicted").inner_text() == "7"
        assert page.locator("#digit-ocr-preview").is_visible()
        checks["drawing_uses_selected_ocr_reader"] = "PASS"
        acceptance = page.evaluate("""async () => {
          const {digitResult} = await import('./v3/digit-readers.js?v=3');
          return ['0','9','O','12','7.',' 7','7 ',''].map(text=>digitResult(text).accepted);
        }""")
        assert acceptance == [True, True, False, False, False, False, False, False]
        checks["no_silent_digit_substitutions_or_text_stripping"] = "PASS"
        page.locator("#files").set_input_files(fixture())
        wait_idle(page)
        record = page.evaluate("digitLab.exportRecord().predictions.at(-1)")
        assert record["predicted"] == 7 and record["raw_text"] == "7"
        assert record["model"] == "Xenova/trocr-small-printed" and record["model_sha256"] is None
        assert record["scores"] is None and record["input_side"] is None
        assert page.locator("#digit-raw").inner_text() == "7"
        checks["printed_upload_and_model_provenance"] = "PASS"
        page.locator("#digit-quality").select_option("precise")
        page.locator("#files").set_input_files(fixture())
        wait_idle(page)
        record = page.evaluate("digitLab.exportRecord().predictions.at(-1)")
        assert record["raw_text"] == "O" and record["predicted"] is None and not record["accepted"]
        assert record["precision"] == "float32"
        page.locator("#digit-reader").select_option("handwritten")
        page.locator("#files").set_input_files(fixture())
        wait_idle(page)
        assert page.locator("#digit-raw").inner_text() == "<b>7</b>"
        assert page.locator("#digit-raw b").count() == 0
        checks["precision_switch_strict_acceptance_and_safe_text"] = "PASS"
        page.locator("#uploads .upload-result").nth(0).click()
        assert page.locator("#digit-reader").input_value() == "printed"
        assert page.locator("#digit-quality").input_value() == "standard"
        assert page.locator("#predicted").inner_text() == "7"
        checks["gallery_restores_reader_and_quality"] = "PASS"
        page.locator("#files").set_input_files([fixture(), fixture()])
        page.locator("#digit-cancel").click()
        wait_idle(page)
        assert "cancelled" in page.locator("#status").inner_text().lower()
        assert page.locator("#classify").is_enabled()
        page.route("**/digit-reader-worker.js*", lambda route: route.fulfill(body="self.onmessage=({data})=>self.postMessage({id:data.id,type:'error',message:'Test download failure'});", content_type="text/javascript"))
        page.locator("#digit-quality").select_option("precise")
        page.locator("#files").set_input_files(fixture())
        wait_idle(page)
        assert page.evaluate("digitLab.exportRecord().predictions.at(-1).error") == "Test download failure"
        assert page.locator("#files").is_enabled()
        checks["batch_cancellation_and_download_error_recovery"] = "PASS"
        page.route("**/digit-reader-worker.js*", lambda route: route.fulfill(body="self.onmessage=()=>{};", content_type="text/javascript"))
        timeout_message = page.evaluate("""async () => {
          const {createDigitReader} = await import('./v3/digit-readers.js?v=3');
          const reader=createDigitReader(()=>{},20);
          try {await reader.read(document.getElementById('drawing'),'printed','standard');}
          catch(error) {return error.message;}
        }""")
        assert "timed out" in timeout_message
        checks["worker_timeout"] = "PASS"
        page.locator("#mode-letters").click()
        assert page.locator("#digit-reader-options").is_hidden() and page.locator("#network").is_visible()
        page.locator("#files").set_input_files({**fixture(), "name": "letter-fixture.png"})
        wait_idle(page)
        assert page.evaluate("digitLab.exportRecord().predictions.at(-1).mode") == "letters"
        page.locator("#uploads .upload-result").nth(0).click()
        assert page.locator("#digit-reader").input_value() == "printed"
        assert page.locator("#scores").is_hidden()
        page.locator("#mode-words").click()
        assert page.locator("#digit-reader-options").is_hidden() and page.locator("#digit-reader-about").is_hidden()
        assert page.locator("#words-workspace").is_visible()
        checks["mixed_gallery_letters_and_words_navigation"] = "PASS"
        page.locator("#mode-digits").click()
        page.locator("#digit-reader").select_option("local")
        page.locator("#files").set_input_files(fixture())
        wait_idle(page)
        assert page.locator("#scores").is_visible() and page.locator("#network").is_visible()
        assert len(page.evaluate("digitLab.exportRecord().predictions.at(-1).scores")) == 10
        checks["cnn_upload_after_ocr"] = "PASS"
        page.unroute("**/digit-reader-worker.js*")
        page.route("**/digit-reader-worker.js*", lambda route: route.fulfill(body=STUB, content_type="text/javascript"))
        for reader in ("ddddocr", "ddddocr-old"):
            page.locator("#digit-reader").select_option(reader)
            assert page.locator("#digit-quality-options").is_hidden()
            page.locator("#files").set_input_files(fixture())
            wait_idle(page)
            record = page.evaluate("digitLab.exportRecord().predictions.at(-1)")
            assert record["predicted"] == 7 and record["precision"] == "float32"
            assert len(record["model_sha256"]) == 64 and record["architecture"] == "captcha-ctc"
            assert record["preprocessing"] == "ddddocr-browser64-v1"
            assert record["decoding"] == "greedy-full-charset-ctc" and record["scores"] is None
            page.locator("#uploads .upload-result").last.click()
            assert page.locator("#digit-reader").input_value() == reader
        checks["captcha_reader_choices_fixed_precision_metadata_and_gallery"] = "PASS"
        page.locator("#digit-reader").select_option("captcha-digits")
        page.locator("#files").set_input_files(fixture())
        wait_idle(page)
        record = page.evaluate("digitLab.exportRecord().predictions.at(-1)")
        assert record["raw_text"] == "X" and record["predicted"] == 7
        assert record["configuration"] == "ctc-digits-v1" and record["decoding"] == "exact-single-digit-ctc-v1"
        assert len(record["scores"]) == 10 and abs(sum(record["scores"]) - 1) < .000001
        assert "conditional digit score" in page.locator("#confidence").inner_text()
        assert page.locator("#digit-raw").inner_text() == "X" and page.locator("#network").is_hidden()
        checks["single_digit_classifier_is_separate_from_unrestricted_transcription"] = "PASS"
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        prefix = Path(args.report).stem
        page.screenshot(path=str(screenshots / (prefix + "-desktop.png")), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(screenshots / (prefix + "-mobile.png")), full_page=True)
        checks["desktop_mobile_no_horizontal_overflow"] = "PASS"
        assert not errors, errors
        assert all(method == "GET" for method, _ in requests)
        checks["no_page_errors_or_upload_requests"] = "PASS"
        if args.live:
            live = browser.new_page()
            live.goto(args.url)
            live.wait_for_function("window.digitLab?.state.ready")
            results = []
            for reader in ("printed", "handwritten"):
                live.locator("#digit-reader").select_option(reader)
                live.locator("#files").set_input_files(fixture())
                live.wait_for_function("!digitLab.state.busy", timeout=300000)
                record = live.evaluate("digitLab.exportRecord().predictions.at(-1)")
                assert "error" not in record, record
                assert "raw_text" in record and record["model"]
                results.append(record)
            report["live"] = {"status": "PASS", "synthetic_smoke_only": True, "results": results}
        report["status"] = "PASS"
        browser.close()
    write_json(destination, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
