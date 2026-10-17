"""Browser/Python parity and end-to-end checks against MNIST and synthetic data."""

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from playwright.sync_api import sync_playwright

from .model import DigitCNN
from .preprocess import prepare
from .train import ROOT, write_json


def open_browser(playwright):
    """Launch an explicit, system or Playwright browser on Windows/Linux."""
    from .platform_support import launch_browser
    (ROOT / ".tmp").mkdir(exist_ok=True)
    tempfile.tempdir = str(ROOT / ".tmp")
    return launch_browser(playwright)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    torch.set_num_threads(2)
    report = {"url": args.url, "checks": {}}
    with sync_playwright() as p:
        browser = open_browser(p)
        context = browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        page = context.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("request", lambda request: requests.append({"url": request.url, "method": request.method}))
        response = page.goto(args.url)
        assert response.status == 200
        page.wait_for_function("window.digitLab?.state.ready === true", timeout=60000)
        fixture = json.loads((ROOT / "dist/model/parity.json").read_text(encoding="utf-8"))
        # Check intermediate activations as well as final logits, across every class.
        parity = page.evaluate("""fixture => fixture.cases.map(item => {
          const result = digitLab.predict(item.input);
          const maxError = (a, b) => Math.max(...a.map((v, i) => Math.abs(v - b[i])));
          return {label: item.label, predicted: result.digit,
            logits: maxError(item.logits, result.logits),
            hidden: maxError(item.hidden, result.hidden),
            pool1: maxError(item.pool1, result.first), pool2: maxError(item.pool2, result.second)};
        })""", fixture)
        assert all(row[k] <= fixture["absolute_tolerance"] for row in parity for k in ["logits", "hidden", "pool1", "pool2"]), parity
        report["checks"]["model_parity"] = {"status": "PASS", "tolerance": fixture["absolute_tolerance"], "cases": parity}

        synthetic = []
        for background, foreground, transparent in [(0, 255, False), (255, 0, False), (255, 0, True)]:
            rgba = np.full((61, 83, 4), background, dtype=np.uint8)
            rgba[:, :, 3] = 0 if transparent else 255
            rgba[12:50, 20:29, :3] = foreground
            rgba[40:50, 20:55, :3] = foreground
            rgba[12:50, 20:29, 3] = 255
            rgba[40:50, 20:55, 3] = 255
            synthetic.append(rgba)
        rng = np.random.default_rng(19)
        colored = np.full((73, 49, 4), [218, 224, 205, 255], dtype=np.uint8)
        colored[10:59, 13:25, :3] = [40, 100, 65]
        colored[15:24, 8:36, :3] = [40, 100, 65]
        synthetic.append(colored)
        # Add soft edges, varying alpha, and non-square dimensions.
        varied = rng.integers(0, 255, (37, 55, 4), dtype=np.uint8)
        varied[:, :, 3] = 255
        varied[[0, -1], :, :3] = 240; varied[:, [0, -1], :3] = 240
        synthetic.append(varied)
        prep_errors = []
        for rgba in synthetic:
            expected = prepare(rgba).flatten()
            actual = page.evaluate("""async item => {
              const {prepareRGBA} = await import('./preprocess.js');
              return Array.from(prepareRGBA(Uint8ClampedArray.from(item.data), item.width, item.height));
            }""", {"data": rgba.flatten().tolist(), "width": rgba.shape[1], "height": rgba.shape[0]})
            error = float(np.max(np.abs(expected - actual)))
            assert error <= 1e-6, error
            prep_errors.append(error)
        report["checks"]["preprocessing_parity"] = {"status": "PASS", "cases": len(synthetic), "maximum_errors": prep_errors, "tolerance": 1e-6}

        model = DigitCNN().eval()
        model.load_state_dict(torch.load(ROOT / "artifacts/best.pt", map_location="cpu", weights_only=True))
        paths = sorted((ROOT / "reports/mnist-fixtures").glob("*.png"))
        assert len(paths) == 10
        page.locator("#files").set_input_files([str(path) for path in paths])
        page.wait_for_function("digitLab.state.uploads.length === 10 && !digitLab.state.busy", timeout=60000)
        records = page.evaluate("digitLab.exportRecord()")
        upload_results = []
        for path, record in zip(paths, records["predictions"]):
            assert "error" not in record, record
            input_image = prepare(np.asarray(Image.open(path).convert("RGBA")))
            np.testing.assert_allclose(record["input"], input_image.flatten(), atol=1e-6)
            with torch.no_grad():
                logits = model(torch.from_numpy(input_image[None]))[0]
                expected_scores = logits.softmax(0).numpy()
            np.testing.assert_allclose(record["scores"], expected_scores, atol=1e-5)
            assert record["predicted"] == int(logits.argmax())
            upload_results.append({"file": path.name, "predicted": record["predicted"],
                                   "score_max_error": float(np.max(np.abs(expected_scores - record["scores"])))})
        report["checks"]["multiple_upload_and_origin_parity"] = {"status": "PASS", "cases": upload_results}

        # Filename independence: identical bytes, unrelated filenames.
        contents = paths[0].read_bytes()
        page.locator("#files").set_input_files([
            {"name": "unrelated-name.png", "mimeType": "image/png", "buffer": contents},
            {"name": "another-name.png", "mimeType": "image/png", "buffer": contents}])
        page.wait_for_function("digitLab.state.uploads.length === 12 && !digitLab.state.busy")
        duplicates = page.evaluate("digitLab.state.uploads.slice(-2)")
        assert duplicates[0]["scores"] == duplicates[1]["scores"]
        assert duplicates[0]["input_sha256"] == duplicates[1]["input_sha256"]
        report["checks"]["filename_independence"] = {"status": "PASS"}

        blank = ROOT / "artifacts/blank.png"
        Image.new("RGB", (50, 50), "white").save(blank)
        page.locator("#files").set_input_files([
            {"name": "blank.png", "mimeType": "image/png", "buffer": blank.read_bytes()},
            {"name": "broken.png", "mimeType": "image/png", "buffer": b"not an image"}])
        page.wait_for_function("digitLab.state.uploads.length === 14 && !digitLab.state.busy")
        invalid = page.evaluate("digitLab.state.uploads.slice(-2)")
        assert all("error" in row and "predicted" not in row for row in invalid)
        report["checks"]["blank_and_invalid_uploads"] = {"status": "PASS", "messages": [row["error"] for row in invalid]}

        page.locator("#clear").click()
        page.locator("#classify").click()
        assert "No visible digit" in page.locator("#status").inner_text()
        box = page.locator("#drawing").bounding_box()
        page.mouse.move(box["x"] + box["width"] * .3, box["y"] + box["height"] * .2)
        page.mouse.down()
        page.mouse.move(box["x"] + box["width"] * .7, box["y"] + box["height"] * .2, steps=8)
        page.mouse.move(box["x"] + box["width"] * .4, box["y"] + box["height"] * .8, steps=12)
        page.mouse.up()
        page.locator("#classify").click()
        assert page.locator("#predicted").inner_text() in list("0123456789")
        assert page.locator("#connections .connection-row").count() == 8
        report["checks"]["pointer_drawing_and_real_visualizations"] = {"status": "PASS", "predicted": page.locator("#predicted").inner_text()}

        with page.expect_download() as download:
            page.locator("#export").click()
        downloaded = ROOT / "artifacts/qa-export.json"
        download.value.save_as(downloaded)
        saved = json.loads(downloaded.read_text(encoding="utf-8"))
        assert len(saved["predictions"]) == 14
        assert saved["model_sha256"] == fixture["model_sha256"]
        report["checks"]["raw_export"] = {"status": "PASS", "records": 14}

        screenshots = ROOT / "reports/screenshots"
        screenshots.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
        report["checks"]["mobile_layout"] = {"status": "PASS", "viewport": [390, 844]}
        assert not errors, errors
        assert not [r for r in requests if not r["url"].startswith(args.url) and not r["url"].startswith("blob:")], requests
        assert all(r["method"] == "GET" for r in requests)
        report["checks"]["browser_only_inference"] = {"status": "PASS", "requests": requests, "page_errors": errors}
        report["model_sha256"] = fixture["model_sha256"]
        report["browser"] = browser.version
        browser.close()
    write_json(ROOT / "reports/browser-qa.json", report)
    print(json.dumps({"checks": len(report["checks"]), "status": "PASS", "report": "reports/browser-qa.json"}), flush=True)


if __name__ == "__main__":
    main()
