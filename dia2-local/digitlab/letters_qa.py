"""Validate actual letter inference, all 26 uploads, and mixed-mode behavior."""

import argparse
import hashlib
import json

import numpy as np
import torch
from PIL import Image
from playwright.sync_api import sync_playwright

from .letters import LABELS, LetterCNN
from .preprocess import prepare
from .qa import open_browser
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765/")
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--report", help="Separate JSON report filename for a later interface release")
    args = parser.parse_args()
    if args.report and ("/" in args.report or "\\" in args.report or not args.report.endswith(".json")):
        parser.error("--report must be a JSON filename")
    report = {"url": args.url, "checks": {}}
    torch.set_num_threads(2)
    digit_manifest = json.loads((ROOT / "dist/model/manifest.json").read_text(encoding="utf-8"))
    letter_manifest = json.loads((ROOT / "dist/model/letters/manifest.json").read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "reports/challenge-freeze.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((ROOT / "dist/model/weights.bin").read_bytes()).hexdigest() == frozen["model_sha256"]
    assert digit_manifest["sha256"] == frozen["model_sha256"]
    report["checks"]["original_digit_weights_preserved"] = {"status": "PASS", "sha256": frozen["model_sha256"]}
    model = LetterCNN().eval()
    model.load_state_dict(torch.load(ROOT / "artifacts/letters/best.pt", map_location="cpu", weights_only=True))
    with sync_playwright() as p:
        browser = open_browser(p)
        context = browser.new_context(viewport={"width": 1440, "height": 1100})
        page = context.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append({"url": request.url, "method": request.method}))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready === true", timeout=60000)
        assert page.evaluate("digitLab.state.mode") == "digits"
        digit_fixture = json.loads((ROOT / "dist/model/parity.json").read_text(encoding="utf-8"))
        digit_parity = page.evaluate("""fixture => fixture.cases.map(item => {
            const result = digitLab.predict(item.input);
            return Math.max(...result.logits.map((v, i) => Math.abs(v - item.logits[i])));
        })""", digit_fixture)
        assert max(digit_parity) <= .0001
        report["checks"]["digit_runtime_regression"] = {"status": "PASS", "maximum_logit_error": max(digit_parity)}
        page.locator("#mode-letters").click()
        page.wait_for_function("digitLab.state.mode === 'letters' && !digitLab.state.loading", timeout=60000)
        assert page.locator("#scores .score-row").count() == 26
        assert page.locator("#mode-letters").get_attribute("aria-pressed") == "true"
        assert "EMNIST Letters" in page.locator("#test-dataset").inner_text()
        assert page.evaluate("digitLab.state.model.labels") == LABELS
        fixture = json.loads((ROOT / "dist/model/letters/parity.json").read_text(encoding="utf-8"))
        parity = page.evaluate("""fixture => fixture.cases.map(item => {
          const result = digitLab.predict(item.input);
          const maxError = (a, b) => Math.max(...a.map((v, i) => Math.abs(v - b[i])));
          return {expected: item.label, predicted: result.label,
            logits: maxError(item.logits, result.logits), hidden: maxError(item.hidden, result.hidden),
            pool1: maxError(item.pool1, result.first), pool2: maxError(item.pool2, result.second),
            score_sum: result.scores.reduce((a, b) => a + b, 0)};
        })""", fixture)
        assert all(row[k] <= .0001 for row in parity for k in ["logits", "hidden", "pool1", "pool2"])
        assert all(abs(row["score_sum"] - 1) < 1e-12 for row in parity)
        report["checks"]["all_26_classes_and_activation_parity"] = {"status": "PASS", "tolerance": .0001,
            "fixture_correct": sum(row["expected"] == row["predicted"] for row in parity), "cases": parity}

        files = sorted((ROOT / "reports/letter-fixtures").glob("*.png"))
        assert len(files) == 26
        page.locator("#files").set_input_files([str(path) for path in files])
        page.wait_for_function("digitLab.state.uploads.length === 26 && !digitLab.state.busy", timeout=60000)
        raw = page.evaluate("digitLab.exportRecord()")
        comparisons = []
        for path, record in zip(files, raw["predictions"]):
            assert "error" not in record, record
            assert record["mode"] == "letters" and record["labels"] == LABELS
            assert record["model_sha256"] == letter_manifest["sha256"]
            prepared = prepare(np.asarray(Image.open(path).convert("RGBA")))
            np.testing.assert_allclose(record["input"], prepared.flatten(), atol=1e-6)
            with torch.no_grad():
                logits = model(torch.from_numpy(prepared[None]))[0]
                scores = logits.softmax(0).numpy()
            assert record["predicted"] == LABELS[int(logits.argmax())]
            np.testing.assert_allclose(record["scores"], scores, atol=1e-5)
            comparisons.append({"file": path.name, "predicted": record["predicted"],
                "maximum_score_error": float(np.max(np.abs(scores - record["scores"])))})
        report["checks"]["26_letter_uploads_and_python_parity"] = {"status": "PASS", "cases": comparisons}

        # Keep character scores and their original model identity valid across mode changes.
        page.locator("#mode-digits").click()
        page.wait_for_function("digitLab.state.mode === 'digits'")
        assert page.locator("#scores .score-row").count() == 10
        assert page.locator("#predicted").inner_text() == "—"
        page.locator("#files").set_input_files(str(ROOT / "reports/mnist-fixtures/digit-0.png"))
        page.wait_for_function("digitLab.state.uploads.length === 27 && !digitLab.state.busy")
        mixed = page.evaluate("digitLab.exportRecord()")
        assert mixed["predictions"][-1]["mode"] == "digits"
        assert mixed["predictions"][-1]["model_sha256"] == digit_manifest["sha256"]
        assert len(mixed["predictions"][-1]["scores"]) == 10
        page.locator(".upload-result").nth(0).click()
        page.wait_for_function("digitLab.state.mode === 'letters'")
        assert page.locator("#predicted").inner_text() == comparisons[0]["predicted"]
        assert page.locator("#scores .score-row").count() == 26
        identity = page.locator(".model-identity")
        if identity.count() and not identity.evaluate("el => el.open"):
            identity.locator("summary").click()
        assert page.locator("#hash").inner_text() == letter_manifest["sha256"]
        report["checks"]["mode_switch_and_saved_result_identity"] = {"status": "PASS", "mixed_records": 27}

        # Exercise pointer drawing through the same shared preparation path.
        page.locator("#clear").click()
        box = page.locator("#drawing").bounding_box()
        for points in [[(.3, .2), (.3, .8)], [(.7, .2), (.7, .8)], [(.3, .5), (.7, .5)]]:
            page.mouse.move(box["x"] + points[0][0] * box["width"], box["y"] + points[0][1] * box["height"])
            page.mouse.down()
            page.mouse.move(box["x"] + points[1][0] * box["width"], box["y"] + points[1][1] * box["height"], steps=12)
            page.mouse.up()
        page.locator("#classify").click()
        assert page.locator("#predicted").inner_text() in LABELS
        assert page.locator("#connections .connection-row").count() == 8
        report["checks"]["letter_drawing_and_visualization"] = {"status": "PASS", "drawn": "H",
            "predicted": page.locator("#predicted").inner_text()}
        with page.expect_download() as download:
            page.locator("#export").click()
        destination = ROOT / "artifacts/letters-qa-export.json"
        download.value.save_as(destination)
        exported = json.loads(destination.read_text(encoding="utf-8"))
        assert exported["schema"] == 2 and len(exported["predictions"]) == 27
        assert exported["predictions"][0]["mode"] == "letters"
        assert exported["predictions"][-1]["mode"] == "digits"
        report["checks"]["mixed_mode_json_export"] = {"status": "PASS"}
        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(exist_ok=True)
        prefix = "public-letters" if args.public else "letters"
        if args.report:
            prefix = args.report.removesuffix(".json")
        page.screenshot(path=str(screenshots / (prefix + "-desktop.png")), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(screenshots / (prefix + "-mobile.png")), full_page=True)
        report["checks"]["letters_mobile_layout"] = {"status": "PASS"}

        # Failed lazy loads must leave the working digit mode usable, then allow retry.
        failure_page = context.new_page()
        failure_page.goto(args.url)
        failure_page.wait_for_function("window.digitLab?.state.ready === true", timeout=60000)
        pattern = "**/model/letters/manifest.json*"
        failure_page.route(pattern, lambda route: route.fulfill(status=503, body="Temporarily unavailable"))
        failure_page.locator("#mode-letters").click()
        failure_page.wait_for_function("!digitLab.state.loading")
        assert failure_page.evaluate("digitLab.state.mode") == "digits"
        assert failure_page.locator("#classify").is_enabled()
        assert "Cannot load the letters model" in failure_page.locator("#status").inner_text()
        failure_page.unroute(pattern)
        failure_page.locator("#mode-letters").click()
        failure_page.wait_for_function("digitLab.state.mode === 'letters' && !digitLab.state.loading", timeout=60000)
        report["checks"]["failed_mode_load_preserves_digits_and_retries"] = {"status": "PASS"}
        failure_page.close()
        assert not errors, errors
        assert all(request["method"] == "GET" and (request["url"].startswith(args.url)
                   or request["url"].startswith("blob:")) for request in requests)
        report["checks"]["no_remote_inference_or_page_errors"] = {"status": "PASS", "requests": requests}
        report["model_sha256"] = letter_manifest["sha256"]
        report["browser"] = browser.version
        browser.close()
    name = "public-letters-browser-qa.json" if args.public else "letters-browser-qa.json"
    if args.report:
        name = args.report
    write_json(ROOT / "reports" / name, report)
    print(json.dumps({"status": "PASS", "checks": len(report["checks"]), "report": name}), flush=True)


if __name__ == "__main__":
    main()
