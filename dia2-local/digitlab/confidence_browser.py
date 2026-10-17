"""Freeze an eligible candidate in an isolated preview and verify actual browser outputs."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .confidence import NAME, digest
from .highres import export
from .preprocess import prepare
from .qa import open_browser
from .residual import ARCHITECTURE, ResidualCNN
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["export", "qa", "official"], required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8878/")
    parser.add_argument("--experiment", choices=[NAME, "captcha-confidence-head-v1"], default=NAME)
    args = parser.parse_args()
    experiment = args.experiment
    directory = ROOT / "artifacts" / experiment
    report = json.loads((ROOT / "reports" / (experiment + ".json")).read_text())
    selection = json.loads((directory / "selection.json").read_text())
    assert selection["selected_epoch"] and digest(directory / "best.pt") == selection["checkpoint_sha256"]
    preview = ROOT / ".tmp" / experiment
    model_dir = preview / "model/captcha-v3/digits"
    if args.stage == "export":
        assert not preview.exists(), "Preserve prior preview"
        # Preview only: preserve the actual source tree and active model exports.
        shutil.copytree(ROOT / "dist", preview, ignore=shutil.ignore_patterns("*.sfc", "roms"))
        for path in model_dir.iterdir():
            # Only the three model files inside this newly copied temporary model folder.
            if path.name in ("weights.bin", "manifest.json", "parity.json"):
                path.unlink()
        model_dir.rmdir()
        model = ResidualCNN()
        model.load_state_dict(torch.load(directory / "best.pt", map_location="cpu", weights_only=True))
        inputs = torch.from_numpy(np.stack([prepare(np.asarray(Image.open(
            ROOT / f"reports/mnist-fixtures/digit-{i}.png").convert("RGBA")), 64) for i in range(10)]))
        assert report.get("independent_test_eligible"), "Only preview a qualified, independently tested candidate"
        training = report | {"test": report["test"]["candidate"]["clean"]}
        manifest = export(model, model_dir, training, inputs)
        manifest["architecture"] = ARCHITECTURE
        write_json(model_dir / "manifest.json", manifest)
        runtime = {str(path.relative_to(preview)): digest(path) for path in [preview / "index.html", *sorted((preview / "v3").glob("*.js"))]}
        freeze = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "checkpoint_sha256": selection["checkpoint_sha256"],
                  "model_sha256": manifest["sha256"], "source_runtime_sha256": runtime,
                  "preprocessing": manifest["preprocessing"], "official_inputs_used": False,
                  "development_selected_epoch": selection["selected_epoch"], "preview_only": True}
        with (directory / "runtime-freeze.json").open("x", encoding="utf-8") as stream:
            json.dump(freeze, stream, indent=2)
        print("PASS: candidate exported and frozen in a separate preview; active exports unchanged")
        return
    freeze = json.loads((directory / "runtime-freeze.json").read_text())
    assert all(digest(preview / name) == value for name, value in freeze["source_runtime_sha256"].items())
    assert digest(model_dir / "weights.bin") == freeze["model_sha256"]
    output = ROOT / "reports" / (experiment + ("-browser.json" if args.stage == "qa" else "-official-followup.json"))
    assert not output.exists(), "Preserve previous evaluation"
    if args.stage == "official":
        assert report.get("independent_test_eligible"), "No official evaluation for a rejected candidate"
        assert json.loads((ROOT / "reports" / (experiment + "-browser.json")).read_text())["status"] == "PASS"
        assert args.url.startswith("http://127.0.0.1:"), "Official inputs stay in the local browser"
    results = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL", "url": args.url,
               "model_sha256": freeze["model_sha256"], "checks": {}, "requests": []}
    torch.set_num_threads(2)
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: results["requests"].append({"url": request.url, "method": request.method}))
            page.goto(args.url)
            page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
            assert page.evaluate("digitLab.state.model.manifest.sha256") == freeze["model_sha256"]
            if args.stage == "qa":
                fixture = json.loads((model_dir / "parity.json").read_text())
                parity = page.evaluate("""fixture => fixture.cases.map(c => {
                  const p=digitLab.predict(c.input), error=(a,b)=>Math.max(...Array.from(a,(x,i)=>Math.abs(x-b[i])));
                  return {logits:error(p.logits,c.logits),hidden:error(p.hidden,c.hidden),
                    first:error(p.first,c.pool1),second:error(p.second,c.pool2)};
                })""", fixture)
                assert all(value <= .0001 for row in parity for value in row.values()), parity
                results["checks"]["actual_activation_parity"] = parity
                paths = sorted((directory / "fixtures").glob("sample-*.png")) if (directory / "fixtures").exists() else sorted((ROOT / "reports/mnist-fixtures").glob("*.png"))
                page.locator("#files").set_input_files([str(path) for path in paths])
                page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=len(paths), timeout=60000)
                records = page.evaluate("digitLab.exportRecord().predictions")
                model = ResidualCNN()
                model.load_state_dict(torch.load(directory / "best.pt", map_location="cpu", weights_only=True))
                model.eval()
                for path, record in zip(paths, records):
                    prepared = prepare(np.asarray(Image.open(path).convert("RGBA")), 64)
                    with torch.no_grad():
                        scores = model(torch.from_numpy(prepared[None])).softmax(1)[0].numpy()
                    np.testing.assert_allclose(record["input"], prepared.flatten(), atol=1e-6)
                    np.testing.assert_allclose(record["scores"], scores, atol=1e-5)
                results["checks"]["real_upload_parity_count"] = len(paths)
            else:
                # Only after independent selection/test and frozen runtime/browser QA.
                paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
                page.locator("#files").set_input_files([str(path) for path in paths])
                page.wait_for_function("digitLab.state.uploads.length === 10 && !digitLab.state.busy", timeout=60000)
                results["raw"] = page.evaluate("digitLab.exportRecord()")
                results["input_sha256"] = {path.name: digest(path) for path in paths}
                results["scope"] = "One frozen-candidate follow-up after prior exposure; not a blind test; no selection or tuning from this result"
                results["checks"]["all_top_scores_at_least_90"] = all(max(row["scores"]) >= .9 for row in results["raw"]["predictions"])
            assert not errors, errors
            assert all(row["method"] == "GET" and (row["url"].startswith(args.url) or row["url"].startswith("blob:")) for row in results["requests"])
            results["checks"]["local_browser_only_inference"] = True
            browser.close()
        results["status"] = "PASS"
    finally:
        with output.open("x", encoding="utf-8") as stream:
            json.dump(results, stream, indent=2)
    print(f"PASS: {args.stage}, model {freeze['model_sha256']}")


if __name__ == "__main__":
    main()
