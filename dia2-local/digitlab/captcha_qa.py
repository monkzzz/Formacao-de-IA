"""Verify synthetic raw uploads end to end, without official challenge images."""

import argparse
import json

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .model import DigitCNN
from .preprocess import prepare
from .qa import open_browser
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8767/")
    parser.add_argument("--experiment", default="captcha-v1")
    parser.add_argument("--report", default="captcha-v1-raw-browser-qa.json")
    args = parser.parse_args()
    if not args.experiment.replace("-", "").isalnum():
        parser.error("Invalid experiment name")
    if (ROOT / "reports" / args.report).exists():
        parser.error("Report exists; preserve evidence with a new --report")
    directory = ROOT / "artifacts" / args.experiment
    manifest = json.loads((ROOT / "dist/model" / args.experiment / "digits/manifest.json").read_text(encoding="utf-8"))
    model = DigitCNN()
    model.load_state_dict(torch.load(directory / "best.pt", map_location="cpu", weights_only=True))
    model.eval()
    torch.set_num_threads(2)
    fixtures = json.loads((directory / "fixtures/labels.json").read_text(encoding="utf-8"))
    report = {"url": args.url, "model_sha256": manifest["sha256"], "checks": {}, "cases": []}
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
        paths = [directory / "fixtures" / row["file"] for row in fixtures]
        page.locator("#files").set_input_files([str(path) for path in paths])
        page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=len(paths), timeout=120000)
        records = page.evaluate("digitLab.exportRecord().predictions")
        maximum = 0
        for path, fixture, record in zip(paths, fixtures, records):
            assert "error" not in record, record
            pixels = prepare(np.asarray(Image.open(path).convert("RGBA")))
            np.testing.assert_allclose(record["input"], pixels.flatten(), atol=1e-6)
            with torch.no_grad():
                logits = model(torch.from_numpy(pixels[None]))[0]
            maximum = max(maximum, float(np.max(np.abs(np.asarray(record["scores"]) - logits.softmax(0).numpy()))))
            assert int(record["predicted"]) == int(logits.argmax())
            assert record["model_sha256"] == manifest["sha256"]
            report["cases"].append({"file": path.name, "expected": fixture["expected"],
                                     "predicted": record["predicted"], "printed": fixture["printed"]})
        assert maximum < 1e-5, maximum
        report["checks"]["raw_upload_python_parity"] = {"count": len(records), "maximum_score_error": maximum}
        # Same pixels under conflicting digit-like names must give identical output.
        data = paths[0].read_bytes()
        page.locator("#files").set_input_files([
            {"name": "digit-0.png", "mimeType": "image/png", "buffer": data},
            {"name": "digit-9.png", "mimeType": "image/png", "buffer": data}])
        page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=len(paths) + 2)
        renamed = page.evaluate("digitLab.state.uploads.slice(-2)")
        assert renamed[0]["scores"] == renamed[1]["scores"]
        report["checks"]["filename_independence"] = True
        # Exercise real drawing and actual feature-map updates.
        page.locator("#drawing").scroll_into_view_if_needed()
        canvas = page.locator("#drawing").bounding_box()
        x, y = canvas["x"] + canvas["width"] * .5, canvas["y"] + canvas["height"] * .2
        page.mouse.move(x, y)
        page.mouse.down()
        page.mouse.move(x, y + canvas["height"] * .6, steps=20)
        page.mouse.up()
        page.locator("#classify").click()
        assert page.locator("#predicted").inner_text().strip() in "0123456789"
        report["checks"]["drawing"] = True
        page.screenshot(path=str(ROOT / "reports/screenshots" / f"{args.experiment}-raw-uploads.png"), full_page=True)
        assert not errors, errors
        report["checks"]["page_errors"] = errors
        browser.close()
    report["status"] = "PASS"
    report["scope"] = "Synthetic upload integration, not a general accuracy benchmark"
    report["sample_correct"] = sum(int(row["predicted"]) == row["expected"] for row in report["cases"])
    write_json(ROOT / "reports" / args.report, report)
    print(f"PASS: {len(fixtures)} raw synthetic uploads, Python parity, filename independence and drawing")


if __name__ == "__main__":
    main()
