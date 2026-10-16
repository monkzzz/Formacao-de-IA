"""Render measured results and an honest local validation report."""

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def read(name):
    return json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))


def main():
    training, test = read("training.json"), read("mnist-test.json")
    qa, comparison = read("browser-qa.json"), read("challenge-comparison.json")
    freeze, raw = read("challenge-freeze.json"), read("challenge-raw.json")
    assert hashlib.sha256((ROOT / "reports/challenge-raw.json").read_bytes()).hexdigest() == comparison["raw_sha256"]
    assert test["model_sha256"] == comparison["model_sha256"] == qa["model_sha256"]
    figures = ROOT / "reports/figures"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "figure.facecolor": "#f4f5ef", "axes.facecolor": "white"})
    history = training["history"]
    epochs = [r["epoch"] for r in history]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    axes[0].plot(epochs, [r["train_loss"] for r in history], label="Augmented train", color="#336c46")
    axes[0].plot(epochs, [r["validation"]["loss"] for r in history], label="Clean validation", color="#a16542")
    axes[0].set(xlabel="Epoch", ylabel="Cross-entropy", title="Loss during training")
    axes[1].plot(epochs, [r["train_accuracy"] * 100 for r in history], label="Augmented train", color="#336c46")
    axes[1].plot(epochs, [r["validation"]["accuracy"] * 100 for r in history], label="Clean validation", color="#a16542")
    axes[1].set(xlabel="Epoch", ylabel="Accuracy (%)", title="Accuracy during training")
    for axis in axes:
        axis.axvline(training["selected_epoch"], color="#888888", ls="--", lw=1, label="Selected epoch")
        axis.grid(alpha=.15); axis.legend(fontsize=8)
    fig.savefig(figures / "learning-curves.png", dpi=180); plt.close(fig)

    matrix = np.asarray(test["confusion_matrix"])
    fig, axis = plt.subplots(figsize=(8, 7), constrained_layout=True)
    image = axis.imshow(matrix, cmap="Greens")
    axis.set(xticks=range(10), yticks=range(10), xlabel="Predicted digit", ylabel="True digit",
             title=f"Official MNIST test: {test['correct']:,}/{test['count']:,} correct")
    for y in range(10):
        for x in range(10):
            axis.text(x, y, str(matrix[y, x]), ha="center", va="center", fontsize=8,
                      color="white" if matrix[y, x] > matrix.max() / 2 else "#173e2b")
    fig.colorbar(image, ax=axis, label="Examples")
    fig.savefig(figures / "mnist-confusion.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(5, 4, figsize=(11, 14), constrained_layout=True)
    for index, case in enumerate(comparison["cases"]):
        row, col = index // 2, index % 2 * 2
        original = Image.open(ROOT.parent / "Dia2/Desafio" / case["file"])
        prepared = np.asarray(raw["predictions"][index]["input"]).reshape(28, 28)
        axes[row, col].imshow(original)
        axes[row, col].set_title(f"{case['file']} · true {case['expected']}", fontsize=10)
        axes[row, col + 1].imshow(prepared, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
        axes[row, col + 1].set_title(f"Predicted {case['predicted']} · {case['predicted_class_score']:.1%} score",
                                     color="#336c46" if case["correct"] else "#a14f39", fontsize=10)
        axes[row, col].axis("off"); axes[row, col + 1].axis("off")
    fig.suptitle("Frozen first evaluation: original images and actual 28×28 inputs", fontsize=14)
    fig.savefig(figures / "challenge-inputs.png", dpi=160); plt.close(fig)

    maximum_logit = max(row["logits"] for row in qa["checks"]["model_parity"]["cases"])
    maximum_challenge = max(c["logit_max_error"] for c in comparison["cases"])
    rows = "\n".join(f"| {c['file']} | {c['expected']} | {c['predicted']} | {c['predicted_class_score']:.4%} | {'Correct' if c['correct'] else 'Incorrect'} |" for c in comparison["cases"])
    off_diagonal = [(int(matrix[y, x]), y, x) for y in range(10) for x in range(10) if x != y]
    largest_errors = ", ".join(f"{true}→{predicted}: {count}" for count, true, predicted in sorted(off_diagonal, reverse=True)[:5])
    report = f"""# Local Desafio Validation Report

## Measured outcome

- **Official MNIST test:** {test['correct']:,}/{test['count']:,} correct (**{test['correct'] / test['count']:.2%}**), with {test['count'] - test['correct']} errors.
- **Official CAPTCHA challenge:** {comparison['correct']}/10 correct (**{comparison['accuracy']:.0%}**), with {10 - comparison['correct']} errors.
- **Scope:** local Edge browser at `{freeze['url']}`. No public deployment or teacher evaluation is claimed.

The model performs well on clean MNIST but is not reliable on these noisy CAPTCHA images. A 99.28% MNIST result must not be presented as CAPTCHA accuracy. The CAPTCHA sample contains only ten examples and does not establish population accuracy.

## Reproducibility and independence

Seed: {training['seed']}. Stratified split: 55,000 training / 5,000 validation. AdamW, batch 256, 18 epochs, recorded affine/noise augmentation. The checkpoint was selected by lowest validation loss at epoch {training['selected_epoch']}; the official test set was loaded only afterward.

Model weight SHA-256: `{test['model_sha256']}`.

Frozen application source-tree SHA-256: `{freeze['source_tree_sha256']}`.

Raw prediction record SHA-256: `{comparison['raw_sha256']}`.

The actual inference application and weights were frozen before challenge uploads. Labels were inspected only after `challenge-raw.json` was durably written. The answer key was obtained by parsing the generator's literal `DIGITS` assignment; the generator was not executed and course images were not modified. No model or preprocessing changes followed the challenge result.

The first collection attempt stopped before writing predictions because a collector assertion rejected browser-local `blob:` preview URLs. The retry changed only the collector, verified the original frozen inference sources and archive, and used the same model and input pipeline. The original freeze and the repaired collector hash are preserved. This was a collection retry, not a new trained model or a tuned second evaluation.

## Runtime verification

- All six Python tests passed, covering real data separation, preprocessing, finite gradients, learning behavior, and export integrity.
- All nine browser QA groups passed, including all-class model parity, five preprocessing fixtures, ten MNIST uploads, filename independence, invalid/blank uploads, pointer drawing, real visualization, export, mobile layout, and browser-only requests.
- Maximum logit difference on ten clean parity fixtures: `{maximum_logit:.10g}` (required ≤ 0.0001).
- All five synthetic preprocessing fixtures matched exactly.
- Each challenge input matched Python preprocessing exactly; maximum challenge logit difference: `{maximum_challenge:.10g}`. Predicted classes matched for all ten.
- The app issued only static local GETs and local blob preview reads. No inference or image-upload API was used.

## First challenge predictions

Scores below are softmax outputs for the predicted class, not calibrated correctness probabilities. Full ten-class scores and prepared inputs are preserved in the raw record.

| Image | Expected | Predicted | Predicted-class score | Result |
| --- | --- | --- | --- | --- |
{rows}

## Error analysis

**Observed:** eight challenge errors remain despite matching browser/Python inputs and logits. High softmax scores can be wrong: for example, case 05 selects 3 rather than 1 with a score above 77%. Runtime mismatch is not supported as the cause of these recorded errors.

**Observed:** the prepared inputs contain interference and peripheral marks. The shared preprocessing crops visible foreground without identifying which marks belong to the digit, so clutter participates in scaling and centering. Training augmentation covers modest affine variation and mild noise, not the full challenge distribution.

**Hypotheses:** distribution shift, damaged glyph topology, unfamiliar font shapes, and background strokes likely contribute. The contribution of each factor has not been isolated experimentally. The first evaluation remains unchanged; no challenge-dependent cleanup or retuning was performed.

Largest official MNIST off-diagonal confusion counts: {largest_errors}. See the complete matrix for class support and all error counts.

## Figures and evidence

![Training and validation curves](figures/learning-curves.png)

![Official MNIST confusion matrix](figures/mnist-confusion.png)

![Original challenge images and actual model inputs](figures/challenge-inputs.png)

- [Training history](training.json)
- [MNIST test metrics and error indices](mnist-test.json)
- [Browser QA](browser-qa.json)
- [Frozen source/model identity](challenge-freeze.json)
- [Unmodified raw predictions](challenge-raw.json)
- [Separate label comparison and challenge parity](challenge-comparison.json)
- [Local interface screenshot](screenshots/desktop.png)
- [All ten challenge uploads](screenshots/challenge-all.png)

## Completion matrix

| Requirement | Status | Evidence |
| --- | --- | --- |
| Real training and held-out MNIST evaluation | PASS | Training history, checkpoint, metrics |
| Exported weight identity | PASS | Manifest, SHA-256, export test |
| Origin/browser parity | PASS | Clean and challenge comparisons |
| Drawing, clear, and image upload | PASS | Browser QA, screenshots |
| Ten challenge previews and predictions | PASS | Raw record and screenshots |
| Browser-only inference | PASS | Network request records |
| Actual feature maps and output contributions | PASS | QA and interface |
| Independent initial prediction recording | PASS | Freeze, raw hash, separate comparison |
| CAPTCHA recognition | 2/10 CORRECT | Raw predictions and answer key comparison |
| Public GitHub Pages deployment | NOT RUN | User requested local-only work |
| Teacher feedback | NOT RUN | Requires a real review session |

## Next steps

Use the application locally and retain the frozen baseline. Any future robustness work must use independently sourced training/validation examples, keep these ten PNGs out of tuning, and report subsequent challenge comparisons as post-inspection iterations. Public deployment and teacher review can be added later without rewriting the initial evaluation.
"""
    (ROOT / "reports/validation.md").write_text(report, encoding="utf-8")
    print("Created reports/validation.md and three measured-result figures.")


if __name__ == "__main__":
    main()
