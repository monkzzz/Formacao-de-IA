"""Render the preserved residual training history without rerunning evaluation."""

import json
import os

from .train import ROOT

os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    report = json.loads((ROOT / "reports/captcha-v3.json").read_text())
    assert not report["status"].startswith("TRAINING"), "Wait for the frozen selection"
    history = report["history"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), layout="constrained")
    for ax, key, title in zip(axes, ("clean", "raw"), ("Clean development", "Independent raw development")):
        baseline = report["baseline_validation"][key]["accuracy"] * 100
        ax.plot([e["epoch"] for e in history], [e[key]["accuracy"] * 100 for e in history],
                marker="o", color="#237655", label="Residual model")
        ax.axhline(baseline, color="#666666", linestyle="--", label="Deployed 64px baseline")
        gate = baseline + (report["policy"]["minimum_raw_gain"] if key == "raw" else -report["policy"]["clean_tolerance"]) * 100
        ax.axhline(gate, color="#b7791f", linestyle=":", label="Eligibility gate")
        if report.get("selected_epoch"):
            ax.axvline(report["selected_epoch"], color="#237655", alpha=.3, linewidth=2)
        ax.set(title=title, xlabel="Epoch", ylabel="Accuracy (%)")
        ax.set_xticks(range(1, len(history) + 1))
        ax.grid(axis="y", alpha=.2)
    axes[1].legend(fontsize=8, loc="lower right")
    fig.suptitle("captcha-v3: validation selects the checkpoint; test data stays separate", fontsize=11)
    destination = ROOT / "docs/images/captcha-v3-training.svg"
    destination.parent.mkdir(exist_ok=True)
    fig.savefig(destination, metadata={"Date": None})
    plt.close(fig)
    print(f"Rendered preserved history: {destination.name}")


if __name__ == "__main__":
    main()
