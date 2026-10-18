"""Fixed visual review, refusal checks and audit of the balanced color run."""

import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

from .balanced_color import DIRECTORY, NAME, REPORT, gates, verify
from .captcha_extension import digest
from .color_preprocess import prepare_color
from .color_study import metrics
from .train import ROOT, write_json


def figures():
    if (ROOT / "reports" / (NAME + "-visual-sample.json")).exists():
        raise FileExistsError("Preserve fixed visual sample")
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for source, offset in (("printed", 0), ("handwritten", 10)):
        fig, axes = plt.subplots(10, 6, figsize=(14, 25))
        for digit in range(10):
            for kind in range(3):
                index = digit + offset + 20 * kind
                rgba = np.asarray(Image.open(DIRECTORY / "train-fixtures" / f"sample-{index:04d}.png").convert("RGBA"))
                axes[digit, 2 * kind].imshow(rgba)
                axes[digit, 2 * kind + 1].imshow(prepare_color(rgba)[0], cmap="gray", vmin=0, vmax=1)
                axes[digit, 2 * kind].set_title(f"{index}: source label {digit}", fontsize=8)
                axes[digit, 2 * kind + 1].set_title(("legacy", "color", "isoluminant")[kind] + " · RGB", fontsize=8)
        for axis in axes.flat:
            axis.axis("off")
        fig.tight_layout()
        destination = ROOT / "reports/screenshots" / (NAME + "-" + source + ".png")
        destination.parent.mkdir(exist_ok=True)
        fig.savefig(destination, dpi=100)
        plt.close(fig)
    write_json(ROOT / "reports" / (NAME + "-visual-sample.json"), {"indices": list(range(60)),
               "selection": "First complete 60-cell block, all ten classes/two sources/three groups; no model errors consulted",
               "independent_human_review": "NOT RUN"})
    print("Fixed raw/RGB printed and handwritten contact sheets written")


def guards():
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    if selection["epoch"]:
        raise ValueError("No-selection guards apply only when no pair qualified")
    rows = []
    for module, stage in (("digitlab.balanced_color", "test"), ("digitlab.balanced_color_browser", "export")):
        result = subprocess.run([sys.executable, "-m", module, "--stage", stage], capture_output=True, text=True)
        rows.append({"module": module, "stage": stage, "returncode": result.returncode,
                     "refused": result.returncode != 0 and "No eligible development pair" in result.stderr})
    untouched = not (DIRECTORY / "test-started.json").exists() and not (ROOT / ".tmp" / (NAME + "-preview")).exists()
    output = ROOT / "reports" / (NAME + "-gates.json")
    if output.exists():
        raise FileExistsError("Preserve completed guards")
    result = {"status": "PASS" if untouched and all(r["refused"] for r in rows) else "FAIL", "checks": rows,
              "reserved_test_and_preview_absent": untouched}
    write_json(output, result)
    if result["status"] != "PASS":
        raise ValueError("Actual no-selection refusal failed")
    print("PASS: actual test/export refusals; reserved sources remain unopened")


def summary():
    d = json.loads(REPORT.read_text())
    verify(d)
    if len(d["history"]) != 4:
        raise ValueError("Complete all four epochs first")
    output = ROOT / "reports" / (NAME + "-summary.md")
    audit_path = ROOT / "reports" / (NAME + "-validation.json")
    if output.exists() or audit_path.exists():
        raise FileExistsError("Preserve completed summary/audit")
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    tests = json.loads((ROOT / "reports" / (NAME + "-unit-tests.json")).read_text())
    checks = {"frozen_sources_assets_fonts_caches": True, "four_epochs": len(d["history"]) == 4,
              "development_report_frozen": digest(DIRECTORY / "development-report.json") == selection["development_sha256"],
              "unit_suite": tests["status"] == "PASS"}
    with np.load(DIRECTORY / "source-split.npz") as split:
        train, validation = set(split["train"]), set(split["validation"])
        checks["disjoint_source_indices"] = not bool(train & validation)
    with np.load(DIRECTORY / "train-clean.npz") as clean:
        checks["clean_training_sources_only"] = set(clean["source_indices"]).issubset(train)
        checks["clean_training_balanced_classes"] = np.bincount(clean["y"], minlength=10).tolist() == [600] * 10
    review = json.loads((ROOT / "reports" / (NAME + "-visual-review.json")).read_text())
    checks["pretraining_visual_review"] = review["status"] == "INSPECTED" and review["allow_training"] and review["fixed_indices"] == list(range(60))
    for filename, split_indices in (("train-records.json", train), ("raw-records.json", validation), ("bridge-records.json", validation)):
        rows = json.loads((DIRECTORY / filename).read_text())
        checks[filename + "_source_membership"] = all(r["source_index"] in split_indices for r in rows if not r["printed"])
        cells = {}
        for row in rows:
            cell = (row["label"], row["printed"], row["kind"])
            cells[cell] = cells.get(cell, 0) + 1
        checks[filename + "_balanced"] = len(set(cells.values())) == 1 and len(cells) == (20 if filename.startswith("bridge") else 60)
    for contract, result in d["baseline_development"].items():
        with np.load(DIRECTORY / ("baseline-" + contract + "-scores.npz")) as scores:
            for group in ("raw", "bridge", "clean"):
                checks[f"baseline_{contract}_{group}_metrics"] = metrics(scores[group], scores[group + "_labels"], scores[group + "_rejected"]) == result[group]
    for row in d["history"]:
        for contract, record in row["contracts"].items():
            actual_gates = {ref: gates(record["metrics"], baseline) for ref, baseline in d["baseline_development"].items()}
            checks[f"epoch_{row['epoch']}_{contract}_gates"] = record["gates"] == actual_gates and record["eligible"] == all(all(c.values()) for c in actual_gates.values())
            with np.load(DIRECTORY / f"epoch-{row['epoch']}-{contract}-scores.npz") as scores:
                for group in ("raw", "bridge", "clean"):
                    actual = metrics(scores[group], scores[group + "_labels"], scores[group + "_rejected"])
                    checks[f"epoch_{row['epoch']}_{contract}_{group}_metrics"] = actual == record["metrics"][group]
    eligible = [(record["metrics"]["raw"]["loss"], row["epoch"], contract)
                for row in d["history"] for contract,record in row["contracts"].items() if record["eligible"]]
    chosen = min(eligible) if eligible else None
    checks["selection_matches_predeclared_minimum"] = ((selection["epoch"], selection["contract"]) == (chosen[1], chosen[2]) if chosen else selection["epoch"] is None and selection["contract"] is None)
    if selection["epoch"]:
        checks["selected_checkpoint"] = digest(DIRECTORY / "best.pt") == selection["checkpoint_sha256"]
        browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
        checks["selected_browser"] = browser["status"] == "PASS" and browser["checkpoint_sha256"] == selection["checkpoint_sha256"]
        if "test" not in d and not d.get("test_overlap"):
            raise ValueError("Complete gated independent test first")
    else:
        checks["actual_no_selection_refusal"] = json.loads((ROOT / "reports" / (NAME + "-gates.json")).read_text())["status"] == "PASS"
    audit = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
             "selected_epoch": selection["epoch"], "selected_contract": selection["contract"],
             "reserved_test": "RUN" if "test" in d else "NOT RUN", "official_followup": "RUN" if "official_followup" in d else "NOT RUN",
             "independent_human_review": "NOT RUN", "active_app_replacement": "NOT RUN", "publication": "NOT RUN"}
    write_json(audit_path, audit)
    if audit["status"] != "PASS":
        raise ValueError("Integrity audit failed")
    lines = ["# Balanced legacy/color training: actual results", "", f"Status: **{d['status']}**. [Predeclared protocol](../docs/balanced-color-training.md).", "",
             "Four CPU epochs; each uses 18,000 balanced synthetic examples (legacy, ordinary color, near-equal-luminance color) "
             "plus 6,000 clean MNIST training examples. One RGB-trained network is evaluated under two preprocessing contracts. "
             "Official inputs/results never enter preparation, training or selection.", "",
             "| Development weights | Preparation | Raw accuracy | Correct >90% | Confident wrong >90% | NLL ↓ | Legacy bridge | Clean MNIST | Eligible against both baselines |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    def table(label, contract, result, passes):
        r = result["raw"]
        return f"| {label} | {contract} | {r['accuracy']:.3%} | {r['correct_above_90_fraction']:.3%} | {r['wrong_above_90_count']} | {r['loss']:.5f} | {result['bridge']['accuracy']:.3%} | {result['clean']['accuracy']:.3%} | {passes} |"
    for contract, result in d["baseline_development"].items():
        lines.append(table("Preserved baseline", contract, result, "—"))
    for row in d["history"]:
        for contract, result in row["contracts"].items():
            lines.append(table(f"EMA epoch {row['epoch']}", contract, result["metrics"], result["eligible"]))
    lines += ["", f"Selected epoch/contract: **{selection['epoch']}/{selection['contract']}**. No gate was relaxed.", ""]
    if not selection["epoch"]:
        lines += ["The last epoch's RGB contract failed: " + "; ".join(ref + " baseline: " + ", ".join(k for k,v in checks.items() if not v)
                  for ref,checks in d["history"][-1]["contracts"]["rgb"]["gates"].items() if not all(checks.values())) + ".", ""]
    if "test" in d:
        lines += ["## Frozen independent evaluation", "", f"Independent gates passed: **{d['independent_test_eligible']}**.", "",
                  "| Configuration | Raw accuracy | Correct >90% | Confident wrong | Bridge | Clean MNIST |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for label, result in [*(('Baseline ' + c, r) for c,r in d["test"]["baselines"].items()), ("Frozen candidate", d["test"]["candidate"])]:
            r = result["raw"]
            lines.append(f"| {label} | {r['accuracy']:.3%} | {r['correct_above_90_fraction']:.3%} | {r['wrong_above_90_count']} | {result['bridge']['accuracy']:.3%} | {result['clean']['accuracy']:.3%} |")
    else:
        lines += ["Reserved test: **NOT RUN**; no development-eligible candidate."]
    lines += ["", "Official follow-up: **" + (str(d["official_followup"]) if "official_followup" in d else "NOT RUN") + "**.", "",
              f"[Full history/provenance]({NAME}.json), [integrity audit]({NAME}-validation.json), [unit suite]({NAME}-unit-tests.json).", "",
              f"[Visual review]({NAME}-visual-review.json): fixed all-class/all-source/all-group sample inspected by the coding agent before training. "
              "Independent human readability review is NOT RUN. Synthetic labels, replay and source separation do not prove every distorted glyph is unambiguous. "
              "History includes font/model/source exposure; these are synthetic development/test figures, not real CAPTCHA population accuracy.", "",
              "The MNIST-only model, earlier extensions and active application remain unchanged. No deployment, CUDA setup, commit or push is part of this run. "
              "Softmax scores are not calibrated correctness probabilities. The professor's criterion remains unmet unless a frozen official follow-up demonstrates all ten correct with every original score strictly >90%.", ""]
    output.write_text("\n".join(lines))
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("figures", "guards", "summary"), required=True)
    args = parser.parse_args()
    {"figures": figures, "guards": guards, "summary": summary}[args.stage]()
