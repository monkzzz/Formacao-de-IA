"""Verify 64px browser calculations, mode displays and inference latency."""

import argparse
import json
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .highres import HighResCNN, export
from .preprocess import prepare
from .qa import open_browser
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8768/")
    parser.add_argument("--report", default="captcha-v2-runtime-qa.json")
    parser.add_argument("--screenshot-prefix", default="captcha-v2")
    parser.add_argument("--development", action="store_true",
                        help="Route a transferred, untrained 64px model for runtime checks before training finishes")
    args = parser.parse_args()
    target = ROOT / "reports" / args.report
    if target.exists():
        parser.error("Preserve existing evidence with a new --report")
    directory = ROOT / "dist/model/captcha-v2/digits"
    if args.development:
        directory = ROOT / "artifacts/highres-runtime-development/digits"
        if not directory.exists():
            model = HighResCNN()
            model.initialize_from(torch.load(ROOT / "artifacts/captcha-v1/best.pt", weights_only=True, map_location="cpu"))
            inputs = torch.from_numpy(np.stack([prepare(np.asarray(Image.open(ROOT / f"reports/mnist-fixtures/digit-{i}.png").convert("RGBA")), 64) for i in range(10)]))
            export(model, directory, {"task": "digits", "test": {"count": 0, "correct": 0, "accuracy": 0},
                                      "split": {"train": 0, "validation": 0}, "status": "Untrained runtime fixture; no accuracy claim"}, inputs)
    manifest = json.loads((directory / "manifest.json").read_text())
    fixture = json.loads((directory / "parity.json").read_text())
    baseline_fixture = json.loads((ROOT / "dist/model/captcha-v1/digits/parity.json").read_text())
    report = {"url": args.url, "model_sha256": manifest["sha256"], "checks": {},
              "scope": "Untrained development runtime fixture" if args.development else "Selected 64px runtime verification"}
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        if args.development:
            page.route("**/model/captcha-v2/digits/manifest.json*", lambda route: route.fulfill(path=str(directory / "manifest.json"), content_type="application/json"))
            page.route("**/model/captcha-v2/digits/weights.bin*", lambda route: route.fulfill(path=str(directory / "weights.bin"), content_type="application/octet-stream"))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
        assert page.evaluate("digitLab.version") == manifest["preprocessing"]
        differences = page.evaluate("""fixture => fixture.cases.map(item => {
          const result = digitLab.predict(item.input);
          const error = (a,b) => Math.max(...Array.from(a, (v,i) => Math.abs(v-b[i])));
          return {label: item.label, logits:error(result.logits,item.logits),
            pool1:error(result.first,item.pool1), pool2:error(result.second,item.pool2),
            hidden:error(result.hidden,item.hidden)};
        })""", fixture)
        assert all(row[key] <= .0001 for row in differences for key in ("logits", "pool1", "pool2", "hidden")), differences
        report["checks"]["activation_parity"] = differences
        pixel_checks = []
        for side in (28, 64):
            for background, foreground, transparent in ((255, 0, False), (0, 255, False), (255, 0, True)):
                rgba = np.full((71, 93, 4), background, np.uint8)
                rgba[:, :, 3] = 0 if transparent else 255
                rgba[9:59, 30:39, :3] = foreground
                rgba[49:59, 30:62, :3] = foreground
                rgba[9:59, 30:39, 3] = 255
                rgba[49:59, 30:62, 3] = 255
                actual = page.evaluate("""async ({data,width,height,side}) => {
                  const {prepareRGBA}=await import('./v3/preprocess.js?v=3.6.0');
                  return Array.from(prepareRGBA(data,width,height,side));
                }""", {"data": rgba.flatten().tolist(), "width": 93, "height": 71, "side": side})
                expected = prepare(rgba, side).flatten()
                np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0)
                pixel_checks.append({"side": side, "background": background, "transparent": transparent,
                                     "maximum_error": float(np.max(np.abs(np.asarray(actual) - expected)))})
        report["checks"]["both_resolution_preprocessing_parity"] = pixel_checks
        assert page.locator("#prepared").get_attribute("width") == "64"
        assert page.locator("#layer-one canvas").first.get_attribute("width") == "32"
        assert page.locator("#layer-two canvas").first.get_attribute("width") == "8"
        assert "64 × 64" in page.locator(".input-preview p").inner_text()
        await_mode = lambda mode: page.evaluate("mode => digitLab.activateMode(mode)", mode)
        await_mode("letters")
        assert page.locator("#prepared").get_attribute("width") == "28"
        assert page.locator("#layer-one canvas").first.get_attribute("width") == "14"
        assert page.locator("#layer-two canvas").first.get_attribute("width") == "7"
        await_mode("words")
        assert page.locator("#words-workspace").is_visible()
        await_mode("digits")
        assert page.locator("#prepared").get_attribute("width") == "64"
        report["checks"]["mode_dimensions_and_words_entry"] = True
        help_text = page.evaluate("""async () => {
          const {answerQuestion}=await import('./v3/helper-knowledge.js?v=3.6.0');
          return answerQuestion('Explain preprocessing').text;
        }""")
        assert "64 × 64" in help_text and "28 × 28" in help_text
        report["checks"]["helper_resolution_explanation"] = True
        legacy = page.evaluate("""async () => {
          const {loadModel}=await import('./v3/inference.js?v=captcha-1');
          const model=await loadModel('digits');
          return {side:model.inputSide,sha256:model.manifest.sha256};
        }""")
        assert legacy == {"side": 28, "sha256": baseline_fixture["model_sha256"]}
        report["checks"]["cached_previous_entry_uses_previous_model"] = True
        timings = page.evaluate("""async ({high,low}) => {
          const {loadModel,predict} = await import('./v3/inference.js?v=captcha-2');
          const old = await loadModel('digits','captcha-v1'), current = digitLab.state.model;
          const measure = (model,cases) => {
            const inputs=cases.map(c => Float32Array.from(c.input)), times=[];
            for (let pass=0;pass<4;pass++) for (const input of inputs) {
              const start=performance.now(); predict(model,input);
              if(pass) times.push(performance.now()-start);
            }
            times.sort((a,b)=>a-b);
            return {count:times.length,median_ms:times[Math.floor(times.length/2)],p95_ms:times[Math.floor(times.length*.95)]};
          };
          return {previous:measure(old,low),high_resolution:measure(current,high)};
        }""", {"high": fixture["cases"], "low": baseline_fixture["cases"]})
        assert timings["high_resolution"]["p95_ms"] < 150, timings
        report["checks"]["desktop_latency"] = timings
        report["latency_scope"] = "Headless desktop Edge on this machine, not a physical-phone benchmark"
        try:
            page.evaluate("digitLab.predict(Array(784).fill(0))")
            raise AssertionError("64px model accepted a 28px tensor")
        except Exception as error:
            assert "4096" in str(error)
        report["checks"]["wrong_input_size_rejected"] = True
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(ROOT / "reports/screenshots" / (args.screenshot_prefix + "-runtime-mobile.png")), full_page=True)
        report["checks"]["mobile_layout"] = True
        assert not errors, errors
        report["checks"]["page_errors"] = errors
        browser.close()
    report["status"] = "PASS"
    write_json(target, report)
    print(json.dumps({"status": "PASS", "latency": timings, "scope": report["scope"]}))


if __name__ == "__main__":
    main()
