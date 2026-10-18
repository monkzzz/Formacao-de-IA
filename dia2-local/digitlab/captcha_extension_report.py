"""Figures, refusal checks and an honest audit summary for the 64px extension."""

import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

from .captcha_extension import DIRECTORY, NAME, POLICY, REPORT, digest, eligible, metrics, read_cache, verify
from .train import ROOT, write_json


def figures():
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    records = json.loads((DIRECTORY / "train-records.json").read_text())
    chosen = [severity * 180 + condition * 30 + source * 10 + (severity * 18 + condition * 3 + source) % 10
              for severity in range(3) for condition in range(6) for source in range(3)]
    inputs, _ = read_cache("train")
    for kind in ("raw", "prepared"):
        output = ROOT / "reports/screenshots" / (NAME + "-" + kind + "-review.png")
        if output.exists():
            raise FileExistsError(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        figure, axes = plt.subplots(9, 6, figsize=(15, 23))
        for axis, index in zip(axes.flat, chosen):
            row = records[index]
            if kind == "raw":
                with Image.open(DIRECTORY / "train-fixtures" / row["file"]) as image:
                    axis.imshow(np.asarray(image))
            else:
                axis.imshow(inputs[index, 0], cmap="gray", vmin=0, vmax=1)
            axis.set_title(f"{index:04d}: {row['label']} · {row['source']}\n{row['condition']} · severity {row['severity']}", fontsize=8)
            axis.axis("off")
        figure.suptitle("Fixed cross-condition training samples · independent human readability review NOT RUN", y=.999)
        figure.tight_layout(rect=(0, 0, 1, .99))
        figure.savefig(output, dpi=110)
        plt.close(figure)
        print(output)
    write_json(ROOT / "reports" / (NAME + "-review-samples.json"),
               {"scope": "Fixed source/condition/severity choices, not selected from model errors", "indices": chosen,
                "source_labels": [records[i]["label"] for i in chosen], "independent_human_review": "NOT RUN"})


def gates():
    metadata = json.loads(REPORT.read_text())
    if metadata.get("selected_epoch") or len(metadata["history"]) != POLICY["epochs"]:
        raise ValueError("Refusal audit is for a completed run with no eligible selection")
    output = ROOT / "reports" / (NAME + "-gates.json")
    if output.exists():
        raise FileExistsError(output)
    rows = []
    for module, stage in (("digitlab.captcha_extension", "test"), ("digitlab.captcha_extension_browser", "export")):
        result = subprocess.run([sys.executable, "-m", module, "--stage", stage], cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        rows.append({"module": module, "stage": stage, "returncode": result.returncode, "output": result.stdout,
                     "status": "PASS" if result.returncode != 0 and "No eligible development selection" in result.stdout else "FAIL"})
    untouched = not (DIRECTORY / "test-started.json").exists() and not (ROOT / ".tmp" / (NAME + "-preview")).exists()
    report = {"status": "PASS" if untouched and all(r["status"] == "PASS" for r in rows) else "FAIL",
              "reserved_test_and_preview_not_created": untouched, "checks": rows}
    write_json(output, report)
    if report["status"] != "PASS":
        raise ValueError("Rejected-model refusal check failed")
    print("PASS: rejected checkpoint cannot export or open reserved test data")


def summary():
    metadata = json.loads(REPORT.read_text())
    if len(metadata["history"]) != POLICY["epochs"]:
        raise ValueError("Complete the fixed four-epoch run first")
    output = ROOT / "reports" / (NAME + "-summary.md")
    audit_path = ROOT / "reports" / (NAME + "-validation.json")
    if output.exists() or audit_path.exists():
        raise FileExistsError("Preserve completed audit")
    verify(metadata)
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    tests = json.loads((ROOT / "reports" / (NAME + "-unit-tests.json")).read_text())
    with np.load(DIRECTORY / "split.npz", allow_pickle=False) as split:
        sources = {key: set(split[key]) for key in ("mnist_train", "mnist_validation", "emnist_train", "emnist_validation")}
    checks = {"sources_fonts_caches_and_preserved_models": True,
              "source_split_indices_disjoint": not bool(sources["mnist_train"] & sources["mnist_validation"] or sources["emnist_train"] & sources["emnist_validation"]),
              "four_epochs_complete": len(metadata["history"]) == POLICY["epochs"],
              "eligible_flags_match_policy": all(r["eligible"] == eligible(r["validation"], metadata["baseline_validation"]) for r in metadata["history"]),
              "frozen_development_report": digest(DIRECTORY / "development-report.json") == selection["development_report_sha256"],
              "unit_tests": tests["status"] == "PASS"}
    for name, count, per_cell in (("train", POLICY["raw_train_count"], 60), ("raw", POLICY["development_count"], 10)):
        records = json.loads((DIRECTORY / (name + "-records.json")).read_text())
        cells = {}
        valid_sources = True
        for row in records:
            cell = (row["label"], row["source"], row["condition"], row["severity"])
            cells[cell] = cells.get(cell, 0) + 1
            if row["source"] != "printed":
                source = row["source"] + ("_train" if name == "train" else "_validation")
                valid_sources &= row["source_index"] in sources[source]
        checks[name + "_balanced_cells"] = len(records) == count and len(cells) == 540 and set(cells.values()) == {per_cell}
        checks[name + "_source_membership"] = bool(valid_sources)
        checks[name + "_geometry_and_gaps"] = all(r["glyph_mass_retained"] >= .99 and r["erased_glyph_fraction"] <= .08 for r in records)
    for row in metadata["history"]:
        with np.load(DIRECTORY / f"epoch-{row['epoch']}-validation-scores.npz", allow_pickle=False) as scores:
            for group in ("raw", "mnist", "emnist", "bridge"):
                _, labels = read_cache(group)
                actual = metrics(scores[group], labels.numpy())
                checks[f"epoch_{row['epoch']}_{group}_counts"] = all(actual[k] == row["validation"][group][k] for k in ("correct", "correct_above_90_count", "wrong_above_90_count"))
    if selection["selected_epoch"]:
        checks["selected_checkpoint"] = digest(DIRECTORY / "best.pt") == selection["checkpoint_sha256"]
        browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
        checks["selected_browser_parity_and_speed"] = (browser["status"] == "PASS"
            and browser["checkpoint_sha256"] == selection["checkpoint_sha256"]
            and browser["p95_ms"] < POLICY["desktop_p95_limit_ms"])
        if "test" in metadata:
            checks["independent_gates_match_policy"] = metadata["independent_test_eligible"] == eligible(
                metadata["test"]["candidate"], metadata["test"]["baseline"])
            checks["reserved_scores_unchanged"] = digest(DIRECTORY / "reserved-scores.npz") == metadata["reserved_scores_sha256"]
            with np.load(DIRECTORY / "reserved-scores.npz", allow_pickle=False) as scores:
                for model in ("baseline", "candidate"):
                    for group in ("raw", "mnist", "emnist", "bridge"):
                        actual = metrics(scores[model + "_" + group], scores[group + "_labels"])
                        checks[f"reserved_{model}_{group}_counts"] = all(actual[k] == metadata["test"][model][group][k]
                            for k in ("correct", "correct_above_90_count", "wrong_above_90_count"))
            if not metadata["independent_test_eligible"]:
                guard = json.loads((ROOT / "reports" / (NAME + "-official-gate.json")).read_text())
                checks["official_refused_after_independent_failure"] = guard["status"] == "PASS" and guard["official_raw_absent"]
        elif not metadata.get("reserved_overlap"):
            raise ValueError("Finish the gated reserved evaluation before reporting completion")
    else:
        guard = json.loads((ROOT / "reports" / (NAME + "-gates.json")).read_text())
        checks["rejected_model_gates"] = guard["status"] == "PASS"
    audit = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
             "selected_epoch": selection["selected_epoch"], "new_reserved_test_run": "test" in metadata,
             "official_followup_run": "official_followup" in metadata, "active_model_replacement": "NOT RUN", "push": "NOT RUN",
             "independent_human_readability_review": "NOT RUN", "publication": "NOT RUN"}
    write_json(audit_path, audit)
    if audit["status"] != "PASS":
        raise ValueError("Extension integrity audit failed")
    base = metadata["baseline_validation"]
    lines = ["# Separate 64px CAPTCHA training extension: actual results", "",
             f"Status: **{metadata['status']}**. [Predeclared protocol](../docs/captcha-training-extension.md). "
             "This study changes training while preserving the original 64px residual architecture and production preprocessing. "
             "Official images, labels, generator and previous official predictions were not used for training or selection.", "",
             "Each of four epochs used 48,600 images: 32,400 balanced independently generated CAPTCHA-style examples, "
             "10,800 clean MNIST examples and 5,400 clean EMNIST examples. The 5,400 raw development images balance ten classes, "
             "three sources, six corruption conditions and three severities. Separate clean validation guards and a legacy bridge "
             "check preservation of earlier skills. Fonts, seed, source indices, data, raw scores and all epoch histories are recorded.", "",
             "| Development model | Raw accuracy | Correct and score >90% | Confident wrong >90% | Raw NLL ↓ | MNIST | EMNIST | Bridge | Eligible |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    def table(label, data, passes):
        r = data["raw"]
        return (f"| {label} | {r['accuracy']:.3%} | {r['correct_above_90_fraction']:.3%} ({r['correct_above_90_count']}) | "
                f"{r['wrong_above_90_count']} | {r['loss']:.5f} | {data['mnist']['accuracy']:.3%} | "
                f"{data['emnist']['accuracy']:.3%} | {data['bridge']['accuracy']:.3%} | {passes} |")
    lines.append(table("Preserved baseline", base, "—"))
    for row in metadata["history"]:
        lines.append(table(f"EMA epoch {row['epoch']}", row["validation"], row["eligible"]))
    lines += ["", f"Frozen selected epoch: **{selection['selected_epoch'] or 'none; retain baseline'}**. "
              "The original MNIST-only and all current selectable models remain unchanged. No development threshold was relaxed "
              "and no epoch was selected using official or reserved results.", ""]
    if "test" in metadata:
        lines += ["## Frozen independent evaluation", "", "| Set | Baseline accuracy | Candidate accuracy | Baseline correct >90% | Candidate correct >90% |",
                  "| --- | ---: | ---: | ---: | ---: |"]
        for group in ("raw", "mnist", "emnist", "bridge"):
            b,c = metadata["test"]["baseline"][group],metadata["test"]["candidate"][group]
            lines.append(f"| {group} | {b['accuracy']:.3%} | {c['accuracy']:.3%} | {b['correct_above_90_fraction']:.3%} | {c['correct_above_90_fraction']:.3%} |")
        lines += ["", f"Independent gates passed: **{metadata['independent_test_eligible']}**. "
                  f"Paired raw changes: {metadata['paired_raw_test']['candidate_only_correct']} candidate-only correct; "
                  f"{metadata['paired_raw_test']['baseline_only_correct']} baseline-only correct. These counts do not by themselves establish statistical significance.", ""]
        bridge_loss = metadata["test"]["baseline"]["bridge"]["accuracy"] - metadata["test"]["candidate"]["bridge"]["accuracy"]
        if bridge_loss > POLICY["gates"]["bridge_accuracy_tolerance"]:
            lines += [f"The legacy-renderer bridge lost **{100 * bridge_loss:.3f} percentage points**, "
                      f"exceeding the allowed **{100 * POLICY['gates']['bridge_accuracy_tolerance']:.3f} points**. "
                      "The candidate is retained as an experimental result; the baseline stays active. "
                      f"[Actual official-stage refusal]({NAME}-official-gate.json) confirms that no official outputs were collected.", ""]
    else:
        if metadata.get("reserved_overlap"):
            lines += [f"Reserved evaluation: **FAIL — exact source pixel overlap**: {metadata['reserved_overlap']}. "
                      "The integrity check stopped evaluation before scoring. No independent test accuracy is claimed.", ""]
        else:
            lines += ["Reserved tests: **NOT RUN**. No rejected candidate is allowed to open reserved partitions or receive another official follow-up.", ""]
    if metadata.get("official_followup"):
        result = metadata["official_followup"]
        lines += [f"Official follow-up after freezing: **{result['correct']}/10 correct**, "
                  f"**{result['correct_above_90']}/10 correct with score strictly >90%**; professor criterion met: **{result['accepted']}**. "
                  f"[Separate raw recording]({NAME}-official-raw.json) and [comparison]({NAME}-official-comparison.json).", ""]
    else:
        lines += ["Official follow-up: **NOT RUN**. No new official confidence result is claimed.", ""]
    lines += ["## Evidence and limits", "",
              f"- [Full history, condition/class matrices and provenance]({NAME}.json).",
              f"- [Integrity audit]({NAME}-validation.json): preserved source/model identities, data hashes, balanced cells, "
              "source membership and saved score counts passed.",
              f"- [Unit suite]({NAME}-unit-tests.json): **{tests['tests_run']} tests passed**.",
              f"- [Browser parity and timing]({NAME}-browser.json)." if selection["selected_epoch"] else "- Browser preview: **NOT RUN**; no eligible checkpoint.",
              f"- [Visual spot-check and ambiguous source record]({NAME}-visual-review.json).",
              f"- [Fixed raw contact sheet](screenshots/{NAME}-raw-review.png) and [actual 64px inputs](screenshots/{NAME}-prepared-review.png).", "",
              "The coding agent visually inspected the fixed sample; independent human readability review is **NOT RUN**. "
              "Annotations bound geometry/gap loss but do not prove every corrupted digit remains unambiguous. Data are generated "
              "CAPTCHA-style images and labelled handwriting, not collected real CAPTCHAs. Font/model/dataset families have prior "
              "exposure; no writer-disjoint, near-duplicate or fresh blind population guarantee is made. "
              "Strict >90% uses unrounded original model scores; these are not calibrated correctness probabilities.", "",
              "Linux CPU execution only; fresh Windows execution, public deployment, active-app replacement and push are **NOT RUN**. "
              "A successful engineering check is separate from the professor's acceptance criterion. The criterion remains unmet "
              "unless a frozen official follow-up actually demonstrates all ten correct with every score strictly >90%.", ""]
    with output.open("x") as stream:
        stream.write("\n".join(lines))
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",choices=("figures","gates","summary"),required=True)
    args = parser.parse_args()
    {"figures":figures,"gates":gates,"summary":summary}[args.stage]()


if __name__ == "__main__":
    main()
