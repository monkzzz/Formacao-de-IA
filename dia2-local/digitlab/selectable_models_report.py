"""Publish measured dataset comparisons and preservation evidence after QA."""

import argparse
import io
import json
import unittest

import numpy as np

from . import supplementary_data as extra
from .data import load_partition
from .supplementary import DIRECTORY, NAME, REPORT, digest
from .train import ROOT, write_json


def unit_tests():
    output = ROOT / "reports/selectable-models-unit-tests.json"
    if output.exists():
        raise FileExistsError(output)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.discover(str(ROOT / "tests")))
    write_json(output, {"status": "PASS" if result.wasSuccessful() else "FAIL",
                       "tests_run": result.testsRun, "errors": len(result.errors),
                       "failures": len(result.failures), "skipped": result.skipped,
                       "output": stream.getvalue()})
    print(stream.getvalue())
    if not result.wasSuccessful():
        raise ValueError("Unit checks failed")


def evaluations():
    report = json.loads(REPORT.read_text())
    if "evaluation" not in report:
        raise ValueError("Complete the frozen supplementary evaluation first")
    entries = (
        ("mnist", ROOT / "dist/model", "Required MNIST-only course model; historical evaluation", "mnist"),
        ("captcha-v3", ROOT / "dist/model/captcha-v3/digits", "Preserved previous default: MNIST + independent synthetic training; historical evaluation", "captcha-v3-preserved"),
        (NAME, ROOT / "dist/model" / NAME / "digits", "Optional MNIST + EMNIST Digits + synthetic extension", NAME),
    )
    for key, folder, scope, filename in entries:
        manifest = json.loads((folder / "manifest.json").read_text())
        data = {"model": key, "model_sha256": manifest["sha256"], "training_scope": scope,
                "mnist_test": manifest["training"]["test"], "official_challenge_for_this_change": "NOT RUN",
                "results_origin": "Preserved model manifest; no new evaluation implied"}
        if key == NAME:
            data.update(results_origin="Frozen supplementary experiment; measured reserved results",
                        evaluations=report["evaluation"], training_sources=manifest["training_sources"],
                        source_counts=report["source_counts"], selected_epoch=report["selected_epoch"])
        output = ROOT / "dist/evaluation" / ("digits-" + filename + ".json")
        if output.exists():
            if json.loads(output.read_text()) != data:
                raise ValueError("Preserve existing evaluation download: " + str(output))
        else:
            write_json(output, data)
        print(output)


def summary():
    output = ROOT / "reports/selectable-models-summary.md"
    audit_path = ROOT / "reports/selectable-models-validation.json"
    if output.exists() or audit_path.exists():
        raise FileExistsError("Preserve completed selectable-model evidence")
    report = json.loads(REPORT.read_text())
    browser = json.loads((ROOT / "reports/selectable-models-browser-qa.json").read_text())
    unit = json.loads((ROOT / "reports/selectable-models-unit-tests.json").read_text())
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    preserved = all(digest(ROOT / name) == value for name, value in report["preserved"].items())
    sources = all(digest(ROOT / "digitlab" / name) == value for name, value in report["source_sha256"].items())
    fonts = all(digest(ROOT / name) == value for name, value in report["fonts_sha256"].items())
    split_hash = digest(DIRECTORY / "split.npz") == report["split_sha256"]
    checkpoint = digest(DIRECTORY / "best.pt") == selection["checkpoint_sha256"]
    # Recheck split membership and exact-pixel separation from canonical sources.
    images, _ = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    test_images, _ = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    e_images, _ = extra.load_partition(True)
    e_test_images, _ = extra.load_partition(False)
    with np.load(DIRECTORY / "split.npz", allow_pickle=False) as split:
        index_disjoint = not (set(split["mnist_train"]) & set(split["mnist_validation"])) and not (set(split["emnist_train"]) & set(split["emnist_validation"]))
        train_hashes = set(extra.fingerprints(e_images[split["emnist_train"]]))
        validation_hashes = set(extra.fingerprints(e_images[split["emnist_validation"]]))
        mnist_hashes = set(extra.fingerprints(images)) | set(extra.fingerprints(test_images))
        test_hashes = set(extra.fingerprints(e_test_images))
        pixel_disjoint = not (train_hashes & (validation_hashes | mnist_hashes | test_hashes)) and not (validation_hashes & (mnist_hashes | test_hashes))
    model = ROOT / "dist/model" / NAME / "digits"
    manifest = json.loads((model / "manifest.json").read_text())
    export_matches = digest(model / "weights.bin") == manifest["sha256"] == report["model_sha256"]
    checks = {"preserved_models": preserved, "training_sources_unchanged": sources,
              "fonts_unchanged": fonts, "split_hash": split_hash, "selected_checkpoint": checkpoint,
              "source_indices_disjoint": index_disjoint, "supplementary_pixels_disjoint": pixel_disjoint,
              "export_weights": export_matches, "browser_qa": browser["status"] == "PASS",
              "unit_tests": unit["status"] == "PASS", "all_epochs_completed": len(report["history"]) == report["policy"]["epochs"]}
    audit = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
             "preserved_sha256": report["preserved"], "supplementary_sha256": manifest["sha256"],
             "model_selection": selection, "official_challenge": "NOT RUN", "public_deployment": "NOT RUN",
             "windows_execution": "NOT RUN", "hosted_ci": "NOT RUN"}
    write_json(audit_path, audit)
    if audit["status"] != "PASS":
        raise ValueError("Dataset/model verification failed")
    lines = ["# Selectable models: measured local results", "",
             "Local v3.11.0 defaults to the preserved MNIST-only course model. The optional extension is a separate experiment. "
             "The previous residual model remains selectable with unchanged weights. "
             "[Dataset boundaries and reproduction](../docs/selectable-models.md). Public deployment: **NOT RUN**.", "",
             f"The extension trained for {report['policy']['epochs']} epochs on {report['training_examples_per_epoch']:,} examples per epoch: "
             "55,000 MNIST + 235,000 EMNIST Digits + 12,000 independent synthetic examples. "
             f"Epoch **{selection['selected_epoch']}** was frozen from validation NLL before test metrics were computed.", "",
             "Both models below were evaluated on the same reserved inputs after that freeze. The synthetic test has 2,400 examples; "
             "EMNIST is real handwriting, not a real CAPTCHA collection. Neither is the ten-image official challenge.", "",
             "| Reserved set | Model | Count | Accuracy | Correct with score ≥90% | NLL ↓ |",
             "| --- | --- | ---: | ---: | ---: | ---: |"]
    for group in ("mnist", "emnist", "synthetic"):
        for key, label in (("mnist_only", "MNIST only"), ("supplementary", "MNIST + supplementary")):
            row = report["evaluation"][key][group]
            lines.append(f"| {group} | {label} | {row['count']:,} | {row['accuracy']:.3%} | {row['correct_at_90_fraction']:.3%} | {row['loss']:.5f} |")
    lines += ["", "This is an optional model comparison, not a claim that the earlier confidence target has been met. "
              "The extension remains selectable even if some measurements regress; its results never overwrite the course model's results. "
              "The original default residual model's 99.10% MNIST result is historical and was not remeasured in this comparison.", "",
              "## Executed validation", "",
              f"- [Unit checks](selectable-models-unit-tests.json): **{unit['tests_run']} passed**.",
              "- [Browser checks](selectable-models-browser-qa.json): actual three-model selection, logits/activation parity, "
              "30 image uploads with Python preprocessing/score parity, mixed-model exports, historical-card restoration, "
              "Letters/Words switching, pretrained-reader separation, failed-load recovery, selected-model drawing, and desktop/mobile selector checks.",
              "- [Integrity audit](selectable-models-validation.json): original model identities, frozen selection, dataset split, "
              "source/font hashes and exported weights passed. Exact duplicate checks do not establish writer or near-duplicate independence.", "",
              "| Model | Desktop median | Desktop p95 |", "| --- | ---: | ---: |"]
    for name, label in (("mnist", "MNIST only"), (NAME, "Supplementary"), ("captcha-v3", "Preserved residual")):
        row = browser["checks"][name + "_latency"]
        lines.append(f"| {label} | {row['median_ms']:.1f} ms | {row['p95_ms']:.1f} ms |")
    lines += ["", "[Desktop screenshot](screenshots/selectable-models-desktop.png) · "
              "[Mobile screenshot](screenshots/selectable-models-mobile.png). Figures and binaries remain ignored local artifacts.", "",
              "No official challenge inference, score rescaling, public deployment, fresh Windows run, hosted CI or teacher approval is claimed. "
              "Use MNIST-only evidence for the required exercise and identify supplementary results as an optional extension. "
              "Scores remain uncalibrated model outputs; test pixels were fingerprinted solely for data hygiene before training. "
              "No test labels or metrics chose the model, and no official challenge input or generator was used.", ""]
    with output.open("x") as stream:
        stream.write("\n".join(lines))
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("unit-tests", "evaluations", "summary"), required=True)
    args = parser.parse_args()
    {"unit-tests": unit_tests, "evaluations": evaluations, "summary": summary}[args.stage]()


if __name__ == "__main__":
    main()
