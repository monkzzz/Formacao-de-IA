"""Publish diagnostic figures and an honest local suite summary from actual records."""

import argparse
import json

import numpy as np
from PIL import Image

from .confidence_suite import ARMS, DIRECTORY, NAME, POLICY, REPORT, digest
from .train import ROOT, write_json


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    diagnostic = json.loads((ROOT / "reports" / (NAME + "-diagnostic.json")).read_text())
    rows = diagnostic["records"]
    conditions = ("clean", "background", "crossing_lines", "blur_jpeg", "short_gaps", "mixed")
    indices = [next(i for i, row in enumerate(rows) if row["condition"] == condition
                    and row["label"] == digit and row["printed"] == printed)
               for condition in conditions for digit, printed in ((2, True), (5, False))]
    with np.load(DIRECTORY / "diagnostic.npz", allow_pickle=False) as cache:
        inputs = cache["views"][indices]
    destination = ROOT / "reports/screenshots" / (NAME + "-diagnostic-readable.png")
    if destination.exists():
        raise FileExistsError(destination)
    figure, axes = plt.subplots(len(indices), 4, figsize=(10, 2.35 * len(indices)))
    for row, index in enumerate(indices):
        prefix = DIRECTORY / "diagnostic-fixtures" / f"sample-{index:03d}"
        with Image.open(str(prefix) + "-raw.png") as image:
            axes[row, 0].imshow(np.asarray(image))
        with Image.open(str(prefix) + "-mask.png") as image:
            axes[row, 1].imshow(np.asarray(image), cmap="gray", vmin=0, vmax=255)
        for column, view in ((2, 0), (3, 2)):
            axes[row, column].imshow(inputs[row, view, 0], cmap="gray", vmin=0, vmax=1)
        label = f"{rows[index]['condition']} · {'printed' if rows[index]['printed'] else 'handwritten'} {rows[index]['label']}"
        axes[row, 0].text(0, -.07, label, transform=axes[row, 0].transAxes, fontsize=8, va="top")
        for column, kind in ((2, "noisy"), (3, "clean")):
            axes[row, column].text(0, -.07, f"Predicted {rows[index][kind + '_prediction']} · score {100 * rows[index][kind + '_top_score']:.1f}%",
                                   transform=axes[row, column].transAxes, fontsize=8, va="top")
        for axis in axes[row]:
            axis.axis("off")
    for axis, title in zip(axes[0], ("Noisy source", "Known glyph mask", "Production 64px input", "Clean-source 64px input")):
        axis.set_title(title, fontsize=10, pad=12)
    figure.suptitle("Independent diagnostic examples · fixed sample choices", y=.995)
    figure.subplots_adjust(top=.97, bottom=.02, left=.02, right=.98, hspace=.3, wspace=.04)
    figure.savefig(destination, dpi=120)
    plt.close(figure)
    print(destination)


def summary():
    metadata = json.loads(REPORT.read_text())
    if metadata["status"] in ("PREPARING", "PREPARED; training/test NOT RUN", "TRAINING"):
        raise ValueError("Complete the fixed training comparison before the final summary")
    diagnostic = json.loads((ROOT / "reports" / (NAME + "-diagnostic.json")).read_text())
    output = ROOT / "reports" / (NAME + "-summary.md")
    if output.exists():
        raise FileExistsError(output)
    baseline = metadata["baseline_validation"]
    lines = ["# Consistency/capacity suite: actual delivery", "",
             f"Status: **{metadata['status']}**. See the [predeclared protocol](../docs/confidence-suite.md) and "
             f"[full measured history]({NAME}.json). This is independent synthetic evidence, not a real-world CAPTCHA accuracy claim.", "",
             "## Preprocessing diagnosis", "",
             f"Across {diagnostic['production_preprocessing']['count']:,} balanced independent examples, the unchanged model scored "
             f"{diagnostic['production_preprocessing']['accuracy']:.2%} on noisy inputs versus "
             f"{diagnostic['clean_source_ablation']['accuracy']:.2%} on the corresponding clean sources. "
             f"The crop window covered {diagnostic['annotation_summary']['crop_glyph_mass_retained']['mean']:.3%} of annotated glyph mass on average, "
             f"but {diagnostic['glyph_under_32_pixels_fraction']:.2%} of glyphs shrank below 32 pixels. "
             "This measures coverage and scale, not preservation of every visible stroke after occlusion. "
             "The small clean/noisy accuracy gap does not justify deploying an unvalidated cleanup rule. "
             "No production preprocessing change was made.", "",
             "The clean-source view is an oracle ablation, not an implementable method for recovering a hidden clean image. "
             "These results do not identify the causes of the four lower-scoring official cases.", "",
             f"[Readable diagnostic contact sheet](screenshots/{NAME}-diagnostic-readable.png) · "
             f"[Per-example annotations and condition results]({NAME}-diagnostic.json)", "",
             "| Diagnostic condition | Accuracy | Correct and score ≥90% |",
             "| --- | ---: | ---: |"]
    for condition, metrics in diagnostic["per_condition"].items():
        lines.append(f"| {condition} | {metrics['accuracy']:.2%} | {metrics['correct_at_90_fraction']:.2%} |")
    lines += ["", "## Matched training comparison", "",
              "The table reports the selected eligible epoch of each arm, when one exists. Otherwise it shows the "
              "lowest-loss rejected development epoch as a diagnostic, not a replacement selection. "
              "All arms received the same data/order and four epochs. Reserved results never change the arm choice.", "",
              "| Arm | Parameters | Epoch shown | Raw accuracy | Correct at ≥90% | Raw NLL | Clean accuracy | Bridge accuracy | Eligible epoch |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
              f"| Preserved baseline | — | — | {baseline['raw']['accuracy']:.3%} | {baseline['raw']['correct_at_90_fraction']:.3%} | "
              f"{baseline['raw']['loss']:.5f} | {baseline['clean']['accuracy']:.3%} | {baseline['bridge']['accuracy']:.3%} | — |"]
    for arm in ARMS:
        result = metadata["arms"][arm]
        row = next((r for r in result["history"] if r["epoch"] == result.get("selected_epoch")),
                   min(result["history"], key=lambda r: r["raw"]["loss"]))
        lines.append(f"| {arm} | {result['parameter_count']:,} | {row['epoch']} | {row['raw']['accuracy']:.3%} | "
                     f"{row['raw']['correct_at_90_fraction']:.3%} | {row['raw']['loss']:.5f} | {row['clean']['accuracy']:.3%} | "
                     f"{row['bridge']['accuracy']:.3%} | {result.get('selected_epoch', 'None')} |")
    lines += ["", f"Frozen choice: **{metadata.get('selected_arm') or 'none; retain baseline'}**. "
              "The deeper arm must satisfy the extra incremental-benefit rule; added capacity alone is not a reason to select it.", "",
              "## Reserved evaluation and official scope", ""]
    if "test" in metadata:
        lines += ["| Reserved measurement | Baseline | Frozen candidate |", "| --- | ---: | ---: |"]
        for group in ("raw", "clean", "bridge"):
            for key in ("accuracy", "correct_at_90_fraction", "loss", "brier", "ece_10_bins"):
                a, b = metadata["test"]["baseline"][group][key], metadata["test"]["candidate"][group][key]
                lines.append(f"| {group}: {key} | {a:.6f} | {b:.6f} |")
        paired = metadata["paired_comparison"]
        lines += ["", f"Paired raw-example changes: candidate-only correct **{paired['candidate_only_correct']}**; "
                  f"baseline-only correct **{paired['baseline_only_correct']}**. "
                  "These counts are not an independent statistical-significance claim."]
    else:
        lines += ["Reserved data: **NOT RUN**. An eligible frozen development selection and matched browser parity/speed "
                  "are required before final data are decoded. No rejected checkpoint is tested on the official images."]
    official = ROOT / "reports" / (NAME + "-official-raw.json")
    lines += ["", f"Official follow-up: {'raw record saved separately; compare only after freezing raw output' if official.exists() else '**NOT RUN**'}. "
              "Prior official exposure remains explicit. No new official confidence score is claimed without that raw record. "
              "No public deployment was performed.", "", "## Preservation and limits", ""]
    if metadata.get("official_followup"):
        result = metadata["official_followup"]
        lines += [f"Official frozen follow-up: {result['correct']}/10 correct; "
                  f"{result['correct_at_90']}/10 correct with score ≥90%; target met: **{result['target_met']}**. "
                  f"[Separate comparison]({NAME}-official-comparison.json).", ""]
    changed = [name for name, value in metadata["preservation"].items() if digest(ROOT / name) != value]
    sources_unchanged = all(digest(ROOT / "digitlab" / n) == h for n, h in metadata["source_sha256"].items())
    datasets_unchanged = all(digest(DIRECTORY / data["file"]) == data["sha256"] for data in metadata["datasets"].values())
    datasets_unchanged = (datasets_unchanged and digest(DIRECTORY / "splits.npz") == metadata["splits_sha256"]
                          and digest(DIRECTORY / "validation-extra.npz") == metadata["extra_sha256"])
    arms_complete = all(len(metadata["arms"][name]["history"]) == POLICY["epochs"] for name in ARMS)
    validation = {"status": "PASS" if not changed and sources_unchanged and datasets_unchanged and arms_complete else "FAIL",
                  "preserved_files_checked": len(metadata["preservation"]),
                  "changed": changed, "sha256": metadata["preservation"],
                  "sources_unchanged": sources_unchanged, "datasets_unchanged": datasets_unchanged,
                  "training_arms_complete": arms_complete,
                  "selection": metadata.get("selected_arm"), "reserved_test_run": "test" in metadata,
                  "official_followup_run": official.exists(), "publication": "NOT RUN"}
    write_json(ROOT / "reports" / (NAME + "-validation.json"), validation)
    lines += [f"Verified {len(metadata['preservation'])} preserved identities: **{'unchanged' if not changed else 'CHANGED: ' + str(changed)}**. "
              f"See [integrity record]({NAME}-validation.json). Datasets, views, weights and figures remain in ignored local storage.", "",
              "The raw diagnostic and raw selection sources are disjoint. The full 5,000 clean validation guard is shared across arms "
              "and includes both raw-source subsets. The font/data generator distribution is synthetic; fonts and MNIST have prior exposure "
              "in historical experiments. Labels are generated/source labels, not independent human readability judgements. "
              "Binned ECE and softmax scores do not establish calibrated real-world correctness probabilities.", "",
              "Linux execution and a portable implementation do not establish a fresh Windows execution or hosted CI pass. "
              "The confidence-on-all-ten target can only be assessed by a properly frozen official follow-up, never by "
              "training against those ten or raising displayed percentages.", ""]
    with output.open("x") as stream:
        stream.write("\n".join(lines))
    print(output)
    if validation["status"] != "PASS":
        raise ValueError("Preservation/source validation failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("figures", "summary"), required=True)
    args = parser.parse_args()
    {"figures": figures, "summary": summary}[args.stage]()


if __name__ == "__main__":
    main()
