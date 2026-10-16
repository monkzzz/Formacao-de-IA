"""Create an evidence-based letter evaluation report and standalone figures."""

import hashlib
import json
import os

from .train import ROOT

os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    read = lambda name: json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))
    training, metrics = read("letters-training.json"), read("letters-test.json")
    qa = read("letters-browser-qa.json")
    matrix = np.asarray(metrics["confusion_matrix"])
    assert matrix.sum() == 20800 and matrix.trace() == metrics["correct"]
    assert all(c["status"] == "PASS" for c in qa["checks"].values())
    original = read("challenge-freeze.json")
    assert hashlib.sha256((ROOT / "dist/model/weights.bin").read_bytes()).hexdigest() == original["model_sha256"]
    raw_hash = hashlib.sha256((ROOT / "reports/challenge-raw.json").read_bytes()).hexdigest()
    assert raw_hash == read("challenge-comparison.json")["raw_sha256"]
    figures = ROOT / "reports/figures"
    labels = metrics["labels"]
    support = matrix.sum(axis=1)
    recalls = matrix.diagonal() / support
    precisions = matrix.diagonal() / np.maximum(1, matrix.sum(axis=0))
    f1 = 2 * precisions * recalls / np.maximum(1e-12, precisions + recalls)
    fig, axis = plt.subplots(figsize=(12, 11), constrained_layout=True)
    display = axis.imshow(matrix, cmap="Greens")
    axis.set(xticks=range(26), yticks=range(26), xticklabels=labels, yticklabels=labels,
             xlabel="Predicted letter", ylabel="True letter",
             title=f"EMNIST Letters official test: {metrics['correct']:,}/{metrics['count']:,} correct")
    for y in range(26):
        for x in range(26):
            if matrix[y, x]:
                axis.text(x, y, str(matrix[y, x]), ha="center", va="center", fontsize=6,
                          color="white" if matrix[y, x] > matrix.max() / 2 else "#173e2b")
    fig.colorbar(display, ax=axis, label="Examples")
    fig.savefig(figures / "letters-confusion.png", dpi=170); plt.close(fig)
    history = training["history"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    epochs = [r["epoch"] for r in history]
    axes[0].plot(epochs, [r["train_loss"] for r in history], label="Augmented training")
    axes[0].plot(epochs, [r["validation"]["loss"] for r in history], label="Clean validation")
    axes[0].set(xlabel="Epoch", ylabel="Cross-entropy", title="Letter training loss")
    axes[1].plot(epochs, [r["train_accuracy"] * 100 for r in history], label="Augmented training")
    axes[1].plot(epochs, [r["validation"]["accuracy"] * 100 for r in history], label="Clean validation")
    axes[1].set(xlabel="Epoch", ylabel="Accuracy (%)", title="Letter training accuracy")
    for axis in axes:
        axis.axvline(metrics["selected_epoch"], color="gray", linestyle="--", label="Selected checkpoint")
        axis.grid(alpha=.15); axis.legend(fontsize=8)
    fig.savefig(figures / "letters-learning.png", dpi=170); plt.close(fig)
    confusion_pairs = sorted([(int(matrix[y, x]), labels[y], labels[x])
                              for y in range(26) for x in range(26) if x != y], reverse=True)[:10]
    worst = ", ".join(f"{a}→{b}: {count}" for count, a, b in confusion_pairs)
    rows = "\n".join(f"| {label} | {int(support[i])} | {precisions[i]:.2%} | {recalls[i]:.2%} | {f1[i]:.2%} |" for i, label in enumerate(labels))
    max_error = max(row["logits"] for row in qa["checks"]["all_26_classes_and_activation_parity"]["cases"])
    public_section = "Public verification has not been recorded for this letter model."
    if (ROOT / "reports/public-letters-browser-qa.json").exists():
        public_letters, public_digits = read("public-letters-browser-qa.json"), read("public-browser-qa-v2.json")
        assert public_letters["model_sha256"] == metrics["model_sha256"]
        assert all(c["status"] == "PASS" for r in [public_letters, public_digits] for c in r["checks"].values())
        public_section = ("The update is published at **https://naoquerosaber.pt/AI/index.html**. "
            "All nine [digit regression groups](public-browser-qa-v2.json) and all ten "
            "[letter verification groups](public-letters-browser-qa.json) passed on the public HTTPS site. "
            "The deployment downloaded and SHA-256-verified every uploaded asset. No training data, parity fixtures, or credentials were uploaded.")
    report = f"""# Letters Mode — Validation

## Measured result

The dedicated A–Z CNN correctly classified **{metrics['correct']:,}/{metrics['count']:,} official EMNIST Letters test examples ({metrics['accuracy']:.2%})**. Macro precision: {precisions.mean():.2%}; macro recall: {recalls.mean():.2%}; macro F1: {f1.mean():.2%}.

The original digit model is unchanged: 99.28% on the official MNIST test. Its original Desafio result remains 2/10. Adding letter recognition does not improve or replace that independent challenge result.

## Data and method

The [official NIST EMNIST Letters dataset](https://www.nist.gov/itl/products-and-services/emnist-dataset) merges uppercase and lowercase forms into 26 classes. Labels are presented as A–Z. This model recognizes one handwritten character at a time; it does not distinguish case or read words.

The NIST archive was verified against the canonical MD5 published in torchvision: `58c8d27c78d21e728a6bc7b3cc06412e`. Extracted file SHA-256 values are recorded in the training provenance. Stored image axes are transposed to upright handwriting; a training-only sample sheet was visually checked before training.

Seed: 20261017. Official training examples: 124,800. Split: 114,400 train / 10,400 validation, reserving 400 per class. Training used {len(history)} epochs, AdamW, batch 256, recorded affine/noise augmentation, and the same preprocessing contract as the browser. The checkpoint was selected at epoch {metrics['selected_epoch']} by minimum validation loss. The 20,800 official test examples were loaded only after selection.

Unreadable official training inputs: {len(training['unreadable_train_indices'])}; unreadable official test inputs: {len(metrics['unreadable_test_indices'])}. Such examples, if present, remain in benchmark counts as zero-input predictions; the interactive app rejects blank uploads rather than inventing a character.

Letter weight SHA-256: `{metrics['model_sha256']}`.

## Browser behavior and correctness

All {len(qa['checks'])} letter QA groups passed. These cover original digit weight identity and runtime parity, all 26 letter outputs and intermediate activations, 26 uploaded examples compared against Python, mode changes and saved-result identity, drawing, mixed-mode export, mobile layout, recovery from a model-loading failure, and browser-only inference.

Maximum letter logit difference on the 26 fixtures: `{max_error:.10g}` (tolerance 0.0001). Each uploaded result identifies its recognition mode, label order, model hash, scores, and prepared pixels. A saved result switches back to its own model when selected, preventing an activation display from using the wrong weights.

{public_section}

Digits and Letters are explicit modes because O/0 and I/1 can be visually ambiguous. A classifier constrained to A–Z will still choose a letter for an out-of-domain input; it is not a general detector of whether an image contains a valid letter. Softmax outputs are not calibrated certainty.

## Per-class official test metrics

| Class | Test examples | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
{rows}

Largest off-diagonal confusion counts: {worst}. These are observed errors; no per-letter accuracy guarantee is made for arbitrary handwriting or fonts.

![Letter training curves](figures/letters-learning.png)

![Official letter test confusion matrix](figures/letters-confusion.png)

## Preserved baseline and release

The original digit model, raw challenge predictions, and frozen application archive were retained. This is a later application version, not a replacement for the first independent challenge evaluation. Original root JavaScript/CSS assets remain available for cached v1 pages; the new interface uses versioned `v2/` assets. Deployment uploads model/dependency assets before switching `index.html`.

## Evidence

- [Training history](letters-training.json)
- [Official test metrics and error indices](letters-test.json)
- [Local browser checks](letters-browser-qa.json)
- [Training orientation check](letters-training-orientation.png)
- [Original digit/Desafio evaluation](validation.md)

Dataset citation: Cohen, Afshar, Tapson, and van Schaik (2017), [EMNIST: an extension of MNIST to handwritten letters](https://arxiv.org/abs/1702.05373).
"""
    (ROOT / "reports/letters-validation.md").write_text(report, encoding="utf-8")
    print(f"Letter report created: {metrics['accuracy']:.2%} test accuracy; macro F1 {f1.mean():.2%}.")


if __name__ == "__main__":
    main()
