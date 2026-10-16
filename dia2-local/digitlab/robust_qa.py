"""Check the active robustness models in the real browser, without CAPTCHA input."""

import argparse
import hashlib
import io
import json

import numpy as np
import torch
from PIL import Image
from playwright.sync_api import sync_playwright

from .letters import LetterCNN
from .model import DigitCNN
from .preprocess import prepare
from .qa import open_browser
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8766/")
    parser.add_argument("--report", default="robust-browser-qa.json",
                        help="Report filename under reports; use a new name for follow-up checks")
    args = parser.parse_args()
    torch.set_num_threads(2)
    report = {"url": args.url, "checks": {}}
    frozen = json.loads((ROOT / "reports/challenge-freeze.json").read_text(encoding="utf-8"))
    original = ROOT / "dist/model/weights.bin"
    assert hashlib.sha256(original.read_bytes()).hexdigest() == frozen["model_sha256"]
    report["checks"]["frozen_digit_model_preserved"] = True
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append({"url": request.url, "method": request.method}))
        response = page.goto(args.url)
        assert response.status == 200
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        count = 0
        for task in ["digits", "letters"]:
            directory = ROOT / "dist/model/robust" / task
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            original_checkpoint = ROOT / ("artifacts/letters/best.pt" if task == "letters" else "artifacts/best.pt")
            assert hashlib.sha256(original_checkpoint.read_bytes()).hexdigest() == manifest["training"]["baseline_checkpoint_sha256"]
            assert hashlib.sha256((directory / "weights.bin").read_bytes()).hexdigest() == manifest["sha256"]
            page.evaluate("task => digitLab.activateMode(task)", task)
            assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
            assert page.evaluate("digitLab.state.model.labels") == manifest["labels"]
            fixture = json.loads((directory / "parity.json").read_text(encoding="utf-8"))
            parity = page.evaluate("""fixture => fixture.cases.map(item => {
                const result = digitLab.predict(item.input);
                const error = (a, b) => Math.max(...Array.from(a, (v, i) => Math.abs(v - b[i])));
                return {label: item.label, logits: error(result.logits, item.logits),
                    hidden: error(result.hidden, item.hidden), pool1: error(result.first, item.pool1),
                    pool2: error(result.second, item.pool2), score_sum: result.scores.reduce((a,b) => a+b, 0)};
            })""", fixture)
            assert all(row[key] <= .0001 for row in parity for key in ["logits", "hidden", "pool1", "pool2"]), parity
            assert all(abs(row["score_sum"] - 1) < 1e-10 for row in parity)
            report["checks"][task + "_activation_parity"] = parity
            model = LetterCNN() if task == "letters" else DigitCNN()
            model.load_state_dict(torch.load(ROOT / "artifacts/robust" / task / "best.pt", weights_only=True, map_location="cpu"))
            model.eval()
            fixtures = ROOT / "reports" / ("letter-fixtures" if task == "letters" else "mnist-fixtures")
            paths = sorted(fixtures.glob("*.png"))
            assert len(paths) == len(manifest["labels"])
            page.locator("#files").set_input_files([str(path) for path in paths])
            count += len(paths)
            page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=count, timeout=60000)
            records = page.evaluate("digitLab.exportRecord().predictions")[-len(paths):]
            for path, record in zip(paths, records):
                assert "error" not in record, record
                assert record["mode"] == task and record["model_sha256"] == manifest["sha256"]
                prepared = prepare(np.asarray(Image.open(path).convert("RGBA")))
                np.testing.assert_allclose(record["input"], prepared.flatten(), atol=1e-6)
                with torch.no_grad():
                    logits = model(torch.from_numpy(prepared[None]))[0]
                expected = manifest["labels"][int(logits.argmax())] if task == "letters" else int(logits.argmax())
                assert record["predicted"] == expected
                np.testing.assert_allclose(record["scores"], logits.softmax(0).numpy(), atol=1e-5)
            assert f"{manifest['training']['test']['accuracy'] * 100:.2f}%" in page.locator("#test-accuracy").inner_text()
            report["checks"][task + "_uploads"] = {"count": len(paths), "scores_match_python": True}
        assert len(page.evaluate("digitLab.exportRecord().predictions")) == 36
        page.locator(".upload-result").first.click()
        page.wait_for_function("digitLab.state.mode === 'digits' && !digitLab.state.loading")
        assert page.evaluate("digitLab.state.model.mode") == "digits"
        report["checks"]["mixed_mode_export"] = True

        blank = io.BytesIO()
        Image.new("RGB", (50, 50), "white").save(blank, format="PNG")
        page.locator("#files").set_input_files([
            {"name": "blank.png", "mimeType": "image/png", "buffer": blank.getvalue()},
            {"name": "broken.png", "mimeType": "image/png", "buffer": b"broken"}])
        page.wait_for_function("digitLab.state.uploads.length === 38 && !digitLab.state.busy")
        assert all("error" in item and "predicted" not in item for item in page.evaluate("digitLab.state.uploads.slice(-2)"))
        report["checks"]["blank_and_invalid_uploads"] = True

        # A failed letter download must preserve the working digit model.
        failure_page = browser.new_page()
        failure_page.goto(args.url)
        failure_page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        pattern = "**/model/robust/letters/manifest.json*"
        failure_page.route(pattern, lambda route: route.fulfill(status=503, body="Unavailable"))
        failure_page.locator("#mode-letters").click()
        failure_page.wait_for_function("!digitLab.state.loading")
        assert failure_page.evaluate("digitLab.state.mode") == "digits"
        assert "Cannot load the letters model" in failure_page.locator("#status").inner_text()
        assert failure_page.locator("#classify").is_enabled()
        failure_page.unroute(pattern)
        failure_page.locator("#mode-letters").click()
        failure_page.wait_for_function("digitLab.state.mode === 'letters' && !digitLab.state.loading", timeout=60000)
        failure_page.close()
        report["checks"]["failed_load_preserves_mode_and_retries"] = True

        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshots / "robust-mobile.png"), full_page=True)
        report["checks"]["mobile_layout"] = True
        assert not errors, errors
        assert all(request["method"] == "GET" and (request["url"].startswith(args.url)
            or request["url"].startswith("blob:")) for request in requests)
        report["checks"]["browser_only_inference"] = True
        report["checks"]["page_errors"] = errors
        browser.close()
    report["status"] = "PASS"
    write_json(ROOT / "reports" / args.report, report)
    print("PASS: digit/letter activations, 36 uploads, mixed export and frozen model integrity")


if __name__ == "__main__":
    main()
