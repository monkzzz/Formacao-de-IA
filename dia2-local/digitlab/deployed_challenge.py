"""Verify a deployed frozen challenge model; never select or tune from results."""

import argparse
from datetime import datetime, timezone
import hashlib
import json

import numpy as np
from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT


def create_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://naoquerosaber.pt/AI/")
    parser.add_argument("--experiment", default="captcha-v2")
    parser.add_argument("--report-prefix", default="release-3.6.0-public-challenge-verification")
    args = parser.parse_args()
    if not args.experiment.replace("-", "").isalnum():
        parser.error("Invalid experiment name")
    raw_path = ROOT / "reports" / (args.report_prefix + "-raw.json")
    report_path = ROOT / "reports" / (args.report_prefix + ".json")
    if raw_path.exists() or report_path.exists():
        parser.error("Preserve earlier verification with a new --report-prefix")
    manifest = json.loads((ROOT / "dist/model" / args.experiment / "digits/manifest.json").read_text())
    freeze = json.loads((ROOT / "reports" / (args.experiment + "-challenge-freeze.json")).read_text())
    assert freeze["model_sha256"] == manifest["sha256"]
    paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        version = page.locator("#app-version").inner_text()
        assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
        page.locator("#files").set_input_files([str(path) for path in paths])
        page.wait_for_function("digitLab.state.uploads.length === 10 && !digitLab.state.busy", timeout=60000)
        raw = page.evaluate("digitLab.exportRecord()")
        assert [row["file"] for row in raw["predictions"]] == [path.name for path in paths]
        assert all("error" not in row and row["model_sha256"] == manifest["sha256"] for row in raw["predictions"])
        raw.update({"verification_url": args.url, "verified_at": datetime.now(timezone.utc).isoformat(),
                    "scope": "Deployed-site verification of an already evaluated frozen model; not an independent test or model selection"})
        create_json(raw_path, raw)
        page.screenshot(path=str(ROOT / "reports/screenshots" / (args.report_prefix + ".png")), full_page=True)
        assert not errors, errors
        browser.close()
    original = json.loads((ROOT / "reports" / (args.experiment + "-challenge-raw.json")).read_text())
    comparison = json.loads((ROOT / "reports" / (args.experiment + "-challenge-comparison.json")).read_text())
    expected = {row["file"]: row["expected"] for row in comparison["cases"]}
    cases = []
    for row, previous in zip(raw["predictions"], original["predictions"]):
        assert row["file"] == previous["file"] and row["predicted"] == previous["predicted"]
        np.testing.assert_allclose(row["input"], previous["input"], atol=1e-6, rtol=0)
        np.testing.assert_allclose(row["scores"], previous["scores"], atol=1e-8, rtol=0)
        cases.append({"file": row["file"], "expected": expected[row["file"]],
                      "predicted": row["predicted"], "correct": int(row["predicted"]) == expected[row["file"]]})
    correct = sum(row["correct"] for row in cases)
    create_json(report_path, {"status": "PASS", "url": args.url, "application_version": version,
        "model_sha256": manifest["sha256"], "scope": raw["scope"],
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "all_predictions_match_frozen_local_evaluation": True, "all_inputs_and_scores_match": True,
        "page_errors": errors, "count": 10, "correct": correct, "accuracy": correct / 10, "cases": cases})
    print(f"PASS: live challenge {correct}/10; all inputs, scores and predictions match frozen local evaluation")


if __name__ == "__main__":
    main()
