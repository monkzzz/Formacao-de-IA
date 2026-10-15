"""Exercise 4: visual evaluation, one calculation at a time."""
from __future__ import annotations
import os
import matplotlib.pyplot as plt
from apoio.evaluation_metrics import (BinaryMetrics, FloatArray, IndexArray, SEED,
    binary_metrics, make_imbalanced_scores, roc_curve, safe_divide)
from apoio.metrics_ui import MetricsInterface, TITLES


def show_metrics() -> None:
    """Open the GUI, or complete the walkthrough without a window."""
    interface = MetricsInterface()
    if os.environ.get("FORMACAO_ML_NO_PAUSE") == "1":
        for _ in range(len(TITLES) - 1):
            interface.advance()
        print("Metricas calculadas:", interface.metrics)
        plt.close(interface.figure)
    else:
        plt.show()


def main() -> None:
    """Launch the evaluation demonstration."""
    show_metrics()


if __name__ == "__main__":
    main()
