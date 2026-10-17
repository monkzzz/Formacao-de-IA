"""Audit and summarize the completed first preprocessing phase."""

import json

import numpy as np

from .preprocessing_preview import PREVIEW
from .preprocessing_study import DIRECTORY, NAME, POLICY, REPORT, digest
from .train import ROOT, write_json


def main():
    output = ROOT / "reports" / (NAME + "-summary.md")
    audit_path = ROOT / "reports" / (NAME + "-validation.json")
    if output.exists() or audit_path.exists():
        raise FileExistsError("Preserve completed study summary")
    metadata = json.loads(REPORT.read_text())
    browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    preview = json.loads((ROOT / "reports" / (NAME + "-preview-freeze.json")).read_text())
    tests = json.loads((ROOT / "reports" / (NAME + "-unit-tests.json")).read_text())
    records = json.loads((DIRECTORY / "records.json").read_text())
    with np.load(DIRECTORY / "source-split.npz", allow_pickle=False) as split:
        train = set(split["emnist_train"])
        development = set(split["emnist_development"])
        split_disjoint = not bool(train & development) and not bool(set(split["mnist_train"]) & set(split["mnist_validation"]))
    counts = {(label, printed): sum(r["label"] == label and r["printed"] == printed for r in records)
              for label in range(10) for printed in (False, True)}
    scores_match = True
    with np.load(DIRECTORY / "scores.npz", allow_pickle=False) as vectors:
        for variant, result in metadata["variants"].items():
            if result["preprocessing_failures"]:
                continue
            for group in ("raw", "clean"):
                scores, labels = vectors[variant + "_" + group], vectors[group + "_labels"]
                correct, high = scores.argmax(1) == labels, scores.max(1) > .9
                metrics = result[group]
                scores_match &= (int(correct.sum()) == metrics["correct"]
                                 and int((correct & high).sum()) == metrics["correct_above_90_count"]
                                 and int((~correct & high).sum()) == metrics["wrong_above_90_count"])
    checks = {
        "preserved_models_app_archive": all(digest(ROOT / n) == h for n,h in metadata["preserved_sha256"].items()),
        "study_sources": all(digest(ROOT / "digitlab" / n) == h for n,h in metadata["source_sha256"].items()),
        "predeclared_protocol": digest(ROOT / "docs/preprocessing-study.md") == metadata["protocol_sha256"],
        "fonts": all(digest(ROOT / n) == h for n,h in metadata["fonts_sha256"].items()),
        "split_file": digest(DIRECTORY / "source-split.npz") == metadata["source_split_sha256"],
        "record_file": digest(DIRECTORY / "records.json") == metadata["records_sha256"],
        "score_file": digest(DIRECTORY / "scores.npz") == metadata["scores_sha256"],
        "raw_fixture_files": all(digest(DIRECTORY / "fixtures" / r["file"]) == r["sha256"] for r in records),
        "source_indices_disjoint": split_disjoint,
        "handwriting_uses_only_development_sources": all(r["source_index"] in development for r in records if not r["printed"]),
        "balanced_digit_source_cells": len(records) == POLICY["development_count"] and set(counts.values()) == {90},
        "strict_counts_match_saved_scores": bool(scores_match),
        "browser_qa": browser["status"] == "PASS" and browser["model_sha256"] == metadata["model_sha256"],
        "preview_files": all(digest(PREVIEW / n) == h for n,h in preview["files"].items()),
        "preview_helper": digest(ROOT / "digitlab/preprocessing_preview.py") == preview["helper_sha256"],
        "preview_uses_frozen_study": digest(REPORT) == preview["study_report_sha256"],
        "unit_tests": tests["status"] == "PASS",
    }
    audit = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
             "selected_variant": metadata["selected_variant"], "model_sha256": metadata["model_sha256"],
             "human_readability_review": "NOT RUN", "reserved_test": "NOT RUN", "official_challenge": "NOT RUN",
             "new_model_training": "NOT RUN", "active_app_replacement": "NOT RUN", "push": "CANCELLED by participant"}
    write_json(audit_path, audit)
    if audit["status"] != "PASS":
        raise ValueError("Study integrity checks failed")
    lines = ["# Fixed-weight preprocessing: first-phase results", "",
             "The preserved 64px residual CNN and its weights were held fixed. All four preparations saw the same new "
             "1,800 balanced independent development examples and 5,000 clean MNIST validation examples. "
             "[Protocol fixed before results](../docs/preprocessing-study.md). "
             "No official challenge input, label, generator or previous prediction cache was used.", "",
             "| Preparation | Raw correct | Raw accuracy | Correct and score >90% | Confident wrong >90% | Raw NLL ↓ | Clean accuracy | Eligible |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for variant, row in metadata["variants"].items():
        if row["preprocessing_failures"]:
            lines.append(f"| {variant} | Preparation failed | — | — | — | — | — | False |")
            continue
        r, c = row["raw"], row["clean"]
        lines.append(f"| {variant} | {r['correct']}/1,800 | {r['accuracy']:.3%} | {r['correct_above_90_count']}/1,800 ({r['correct_above_90_fraction']:.3%}) | {r['wrong_above_90_count']} | {r['loss']:.5f} | {c['accuracy']:.3%} | {row['eligible']} |")
    lines += ["", f"Frozen development choice: **{metadata['selected_variant']}**. "
              "Small-component cleanup produced 24 more correct predictions above 90%, one fewer correct prediction overall, "
              "and one fewer confident incorrect prediction. Its 0.056-point raw accuracy loss is within the predeclared "
              "0.1-point tolerance. Clean accuracy is unchanged; raw NLL improves. "
              "This is a measured trade-off, not an across-the-board accuracy improvement.", "",
              "Median filtering improves raw accuracy but drops clean accuracy by 1.28 percentage points and increases confident errors; "
              "it is rejected. Median background estimation does not improve strict confidence coverage enough to qualify.", "",
              "## Browser and preservation", "",
              f"[Unit checks]({NAME}-unit-tests.json): **{tests['tests_run']} passed**. "
              f"[Isolated browser parity]({NAME}-browser.json): **60 development uploads passed**, "
              f"maximum input error {browser['preprocessing_max_error']}, maximum score error {browser['scores_max_error']:.3g}, "
              f"real activation parity passed; desktop median inference {browser['median_inference_ms']:.1f} ms and "
              f"p95 {browser['p95_inference_ms']:.1f} ms. This is an isolated runtime harness, not an active-app deployment.", "",
              f"[Integrity audit]({NAME}-validation.json) checks source and raw fixture hashes, source splits, "
              "font hashes, saved scores, preview assets and unchanged existing model/app identities. "
              f"[Actual recorded history]({NAME}.json).", "",
              f"[Fixed raw/prepared examples](screenshots/{NAME}-inputs.png). These were inspected visually by the coding agent; "
              "independent human readability review remains **NOT RUN**. Labels come from source datasets and rendered classes. "
              "This synthetic/font distribution is not a collected real CAPTCHA population, and source-index separation does not "
              "establish writer or near-duplicate independence.", "",
              "## Next boundary", "",
              "The selected preparation is a development candidate only. Reserved data and the official ten remain unopened in this study. "
              "A separately frozen training extension can now compare the preserved 64px model against representative CAPTCHA-style "
              "training with this preparation. Final independent evaluation must come after model selection; official outcomes must never "
              "choose another transformation, epoch or model. Keep the MNIST-only course model and all current selectable models intact.", "",
              "No new model training, active-app replacement, official challenge run, deployment or push was performed. "
              "The participant cancelled pushing. The professor's 10/10 correct and every score strictly >90% target is still **unmet**; "
              "these development figures do not establish it.", ""]
    with output.open("x") as stream:
        stream.write("\n".join(lines))
    print(output)


if __name__ == "__main__":
    main()
