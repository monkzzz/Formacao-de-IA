"""Build an aggregate public summary after a frozen final evaluation."""

import argparse
import hashlib
import json

from .train import ROOT, write_json


def metrics(value):
    return {key: value[key] for key in ("count", "correct", "accuracy")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", default="captcha-v2")
    parser.add_argument("--version", default="3.6.0")
    args = parser.parse_args()
    if not args.experiment.replace("-", "").isalnum():
        parser.error("Invalid experiment name")
    target = ROOT / "dist/evaluation" / f"digits-{args.experiment}.json"
    if target.exists():
        parser.error("Public summary already exists; preserve the frozen release")
    report = json.loads((ROOT / "reports" / f"{args.experiment}.json").read_text())
    comparison = json.loads((ROOT / "reports" / f"{args.experiment}-challenge-comparison.json").read_text())
    manifest = json.loads((ROOT / "dist/model" / args.experiment / "digits/manifest.json").read_text())
    freeze_path = ROOT / "reports" / f"{args.experiment}-challenge-freeze.json"
    previous = json.loads((ROOT / "reports/captcha-v1-challenge-comparison.json").read_text())
    assert report["model_sha256"] == comparison["model_sha256"] == manifest["sha256"]
    assert report["policy"]["challenge_inputs_used"] is False
    write_json(target, {"application_version": args.version, "model_sha256": manifest["sha256"],
        "input_side": manifest.get("input_side", 28), "preprocessing": manifest["preprocessing"],
        "selection_epoch": report["selected_epoch"], "clean_mnist": metrics(report["test"]),
        "raw_synthetic": metrics(report["raw_test"]),
        "previous_clean_mnist": metrics(report["baseline_test"]["clean"]),
        "previous_model_on_same_raw_synthetic": metrics(report["baseline_test"]["raw"]),
        "official_challenge": metrics(comparison), "previous_challenge": metrics(previous),
        "scope": "Follow-up evaluation; prior challenge outcomes known, not a fresh blind test. Raw synthetic data is broader than the v3.5.0 benchmark. Synthetic and clean scores do not establish real CAPTCHA population accuracy.",
        "challenge_used_for_training_or_selection": False, "challenge_raw_sha256": comparison["raw_sha256"],
        "freeze_sha256": hashlib.sha256(freeze_path.read_bytes()).hexdigest()})
    print(f"Wrote aggregate-only public evaluation summary: {target.name}")


if __name__ == "__main__":
    main()
