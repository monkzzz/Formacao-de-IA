"""Exercise actual dataset selection, parity, uploads and recovery in a browser."""

import argparse
import json
from urllib.parse import urlparse

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .preprocess import prepare
from .qa import open_browser
from .qa_outputs import qa_outputs, qa_report
from .residual import ResidualCNN
from .supplementary import NAME, original_model
from .train import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8882/")
    parser.add_argument("--report", default="selectable-models-browser-qa.json")
    parser.add_argument("--screenshot-prefix", default="selectable-models")
    args = parser.parse_args()
    output, captures = qa_outputs(args.report, args.screenshot_prefix)
    torch.set_num_threads(2)
    checks, errors, requests = {}, [], []
    report = {"status": "FAIL", "url": args.url, "checks": checks,
              "official_challenge": "NOT RUN", "public_deployment": "NOT RUN"}
    with qa_report(output, report):
        folders = {"mnist": ROOT / "dist/model",
                   "captcha-v3": ROOT / "dist/model/captcha-v3/digits"}
        manifests = {key: json.loads((path / "manifest.json").read_text()) for key, path in folders.items()}
        paths = sorted((ROOT / "artifacts" / NAME / "fixtures").glob("sample-*.png"))[:10]
        assert len(paths) == 10
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append({"url": request.url, "method": request.method}))
            page.goto(args.url)
            page.wait_for_function("window.digitLab?.state.ready && !digitLab.state.loading", timeout=60000)
            assert page.evaluate("digitLab.state.digitExperiment") == "mnist"
            assert page.locator("#cnn-model").input_value() == "mnist"
            checks["mnist_only_default"] = {"status": "PASS", "sha256": page.evaluate("digitLab.state.model.manifest.sha256")}
            assert checks["mnist_only_default"]["sha256"] == manifests["mnist"]["sha256"]
            count = 0
            for experiment, folder in folders.items():
                page.locator("#cnn-model").select_option(experiment)
                page.wait_for_function("key => digitLab.state.digitExperiment === key && !digitLab.state.loading", arg=experiment)
                assert page.evaluate("digitLab.state.model.manifest.sha256") == manifests[experiment]["sha256"]
                fixture = json.loads((folder / "parity.json").read_text())
                parity = page.evaluate("""fixture => fixture.cases.map(item => {
                  const actual = digitLab.predict(item.input);
                  const delta = (a,b) => Math.max(...Array.from(a,(v,i) => Math.abs(v-b[i])));
                  return {logits: delta(actual.logits,item.logits), hidden: delta(actual.hidden,item.hidden),
                    pool1: delta(actual.first,item.pool1), pool2: delta(actual.second,item.pool2)};
                })""", fixture)
                assert all(v <= .0001 for row in parity for v in row.values()), parity
                checks[experiment + "_activations"] = {"status": "PASS", "cases": len(parity), "maximum_errors": parity}
                expected = manifests[experiment]["training"]["test"]
                assert f"{expected['accuracy'] * 100:.2f}%" in page.locator("#test-accuracy").inner_text()
                assert f"{expected['accuracy'] * 100:.2f}" in page.locator("#benchmark-digits strong").inner_text()
                evaluation = page.locator("#digit-evaluation-link").get_attribute("href")
                response = page.request.get(args.url.rstrip("/") + "/" + evaluation.removeprefix("./"))
                assert response.ok
                assert response.json()["model_sha256"] == manifests[experiment]["sha256"]
                network = original_model() if experiment == "mnist" else ResidualCNN() if experiment == "captcha-v3" else original_model()
                if experiment != "mnist":
                    network.load_state_dict(torch.load(ROOT / "artifacts" / experiment / "best.pt", map_location="cpu", weights_only=True))
                network.eval()
                page.locator("#files").set_input_files([str(path) for path in paths])
                count += len(paths)
                page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=count, timeout=120000)
                records = page.evaluate("digitLab.state.uploads.slice(-10)")
                maximum = 0
                for path, record in zip(paths, records):
                    assert "error" not in record, record
                    assert record["cnn_model"] == experiment
                    assert record["model_sha256"] == manifests[experiment]["sha256"]
                    pixels = prepare(np.asarray(Image.open(path).convert("RGBA")), manifests[experiment].get("input_side", 28))
                    np.testing.assert_allclose(record["input"], pixels.flatten(), atol=1e-6)
                    with torch.no_grad():
                        scores = network(torch.from_numpy(pixels[None])).softmax(1)[0].numpy()
                    np.testing.assert_allclose(record["scores"], scores, atol=1e-5)
                    maximum = max(maximum, float(np.max(np.abs(scores - record["scores"]))))
                checks[experiment + "_uploads_and_identity"] = {"status": "PASS", "cases": len(records), "maximum_score_error": maximum}
                # Warmed CPU inference timings, independent of upload/decode time.
                timings = page.evaluate("""input => {
                  digitLab.predict(input);
                  return Array.from({length:30}, () => {const t=performance.now();digitLab.predict(input);return performance.now()-t;});
                }""", fixture["cases"][0]["input"])
                checks[experiment + "_latency"] = {"status": "PASS", "median_ms": float(np.median(timings)), "p95_ms": float(np.percentile(timings, 95)), "scope": "Measured desktop only; not a model promotion gate"}
            exported = page.evaluate("digitLab.exportRecord()")
            assert {r["cnn_model"] for r in exported["predictions"]} == set(folders)
            checks["mixed_model_session_export"] = {"status": "PASS", "records": len(exported["predictions"])}
            page.locator(".upload-result").first.click()
            page.wait_for_function("digitLab.state.digitExperiment === 'mnist' && !digitLab.state.loading")
            assert page.locator("#cnn-model").input_value() == "mnist"
            assert page.evaluate("digitLab.state.model.manifest.sha256") == manifests["mnist"]["sha256"]
            checks["old_upload_restores_its_model"] = {"status": "PASS"}
            page.locator("#mode-letters").click()
            page.wait_for_function("digitLab.state.mode === 'letters' && !digitLab.state.loading")
            assert not page.locator("#cnn-model-options").is_visible()
            letter_fixture = json.loads((ROOT / "dist/model/robust/letters/parity.json").read_text())
            assert page.evaluate("digitLab.state.model.manifest.sha256") == letter_fixture["model_sha256"]
            delta = page.evaluate("""fixture => Math.max(...fixture.cases.map(item => {
              const result=digitLab.predict(item.input);
              return Math.max(...result.logits.map((v,i)=>Math.abs(v-item.logits[i])));
            }))""", letter_fixture)
            assert delta <= .0001
            checks["letters_preserved"] = {"status": "PASS", "maximum_logit_error": delta}
            page.locator("#mode-words").click()
            assert page.locator("#words-workspace").is_visible()
            page.locator("#mode-digits").click()
            page.wait_for_function("digitLab.state.mode === 'digits' && !digitLab.state.loading")
            assert page.locator("#cnn-model").input_value() == "mnist"
            checks["words_and_mode_roundtrip"] = {"status": "PASS"}
            page.locator("#digit-reader").select_option("captcha-digits")
            assert not page.locator("#cnn-model-options").is_visible()
            page.locator("#digit-reader").select_option("local")
            assert page.locator("#cnn-model-options").is_visible()
            checks["pretrained_readers_remain_separate"] = {"status": "PASS"}
            # Drop cache and reject one actual model fetch. Working MNIST must survive.
            page.evaluate("key => delete digitLab.state.models['digits:' + key]", "captcha-v3")
            page.route("**/model/captcha-v3/digits/manifest.json*", lambda route: route.fulfill(status=503, body="unavailable"))
            page.locator("#cnn-model").select_option("captcha-v3")
            page.wait_for_function("!digitLab.state.loading")
            assert page.locator("#status").evaluate("el => el.classList.contains('error')")
            assert page.locator("#cnn-model").input_value() == "mnist"
            assert page.evaluate("digitLab.state.model.manifest.sha256") == manifests["mnist"]["sha256"]
            page.unroute("**/model/captcha-v3/digits/manifest.json*")
            page.locator("#cnn-model").select_option("captcha-v3")
            page.wait_for_function("key => digitLab.state.digitExperiment === key && !digitLab.state.loading", arg="captcha-v3")
            checks["failed_load_keeps_previous_model_and_retry_works"] = {"status": "PASS"}
            page.evaluate("""() => {const c=document.getElementById('drawing'),ctx=c.getContext('2d');
              ctx.fillStyle='white';ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle='black';
              ctx.fillRect(c.width*.4,c.height*.2,20,c.height*.6);
            }""")
            drawing = page.evaluate("digitLab.predict(Array.from(digitLab.prepareCanvas(document.getElementById('drawing')))).label")
            page.locator("#classify").click()
            page.wait_for_function("!digitLab.state.busy")
            assert page.locator("#predicted").inner_text() == drawing
            checks["drawing_uses_selected_weights"] = {"status": "PASS"}
            page.locator("#workspace").scroll_into_view_if_needed()
            page.screenshot(path=str(captures["desktop"]))
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.locator("#cnn-model").is_visible()
            page.screenshot(path=str(captures["mobile"]))
            checks["desktop_mobile_selector"] = {"status": "PASS", "mobile_width": 390}
            assert not errors, errors
            origin = urlparse(args.url).netloc
            assert all(row["method"] == "GET" and (urlparse(row["url"]).netloc == origin or row["url"].startswith(("blob:", "data:"))) for row in requests), requests
            checks["browser_only_static_requests"] = {"status": "PASS", "requests": len(requests), "page_errors": errors}
            report["status"] = "PASS"
            browser.close()
    print(output)


if __name__ == "__main__":
    main()
