"""Validated binary metrics and fixed synthetic examples shared with the slides."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IndexArray = NDArray[np.int64]
SEED = 7


@dataclass(frozen=True)
class BinaryMetrics:
    """Confusion counts and metrics; undefined ratios use zero."""
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    accuracy: float
    precision: float
    recall: float
    f1: float


@dataclass(frozen=True)
class MetricScenario:
    """Fixed labels and scores for a didactic example."""
    name: str
    labels: IndexArray
    scores: FloatArray


def safe_divide(numerator: float, denominator: float) -> float:
    """Use zero when a metric has no cases in its denominator."""
    return numerator / denominator if denominator else 0.0


def validate_labels(labels: IndexArray) -> None:
    """Require a nonempty binary vector at the public boundary."""
    if labels.ndim != 1 or not labels.size or not np.isin(labels, (0, 1)).all():
        raise ValueError("Esperado um vetor não vazio de labels 0/1.")


def binary_metrics(labels: IndexArray, predictions: IndexArray) -> BinaryMetrics:
    """Derive confusion counts, accuracy, precision, recall and F1."""
    validate_labels(labels)
    if labels.shape != predictions.shape:
        raise ValueError("labels e predictions devem ter o mesmo tamanho.")
    validate_labels(predictions)
    tp = int(((labels == 1) & (predictions == 1)).sum())
    fp = int(((labels == 0) & (predictions == 1)).sum())
    fn = int(((labels == 1) & (predictions == 0)).sum())
    tn = int(((labels == 0) & (predictions == 0)).sum())
    precision, recall = safe_divide(tp, tp + fp), safe_divide(tp, tp + fn)
    return BinaryMetrics(tp, fp, fn, tn, (tp + tn) / labels.size, precision,
                         recall, safe_divide(2 * tp, 2 * tp + fp + fn))


def roc_curve(labels: IndexArray, scores: FloatArray) -> tuple[FloatArray, FloatArray, float]:
    """Group tied scores at one threshold and compute trapezoidal AUC."""
    validate_labels(labels)
    if scores.shape != labels.shape or not np.isfinite(scores).all():
        raise ValueError("Os scores devem ser finitos e ter a mesma forma dos labels.")
    positives, negatives = int(labels.sum()), int((1 - labels).sum())
    if not positives or not negatives:
        raise ValueError("A curva ROC precisa de exemplos positivos e negativos.")
    thresholds = np.concatenate(([np.inf], np.sort(np.unique(scores))[::-1]))
    tpr = np.array([((scores >= t) & (labels == 1)).sum() / positives for t in thresholds])
    fpr = np.array([((scores >= t) & (labels == 0)).sum() / negatives for t in thresholds])
    return fpr, tpr, float(np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2))


def make_imbalanced_scores(seed: int = SEED, size: int = 1000,
                           positive_rate: float = .05) -> tuple[IndexArray, FloatArray]:
    """Preserve the original seeded example for numerical callers."""
    if size < 1 or not 0 < positive_rate < 1:
        raise ValueError("size deve ser positivo e positive_rate deve estar entre 0 e 1.")
    random = np.random.default_rng(seed)
    labels = (random.random(size) < positive_rate).astype(np.int64)
    return labels, np.clip(random.normal(.25 + .4 * labels, .18), 0, 1)


def metric_scenarios() -> tuple[MetricScenario, ...]:
    """Return the slide examples and a rare-class accuracy trap."""
    labels = np.concatenate((np.ones(20, dtype=np.int64), np.zeros(80, dtype=np.int64)))
    scores = np.concatenate((np.linspace(.55, .95, 16), np.linspace(.1, .45, 4),
                             np.linspace(.51, .65, 8), np.linspace(.02, .49, 72)))
    order = np.random.default_rng(SEED).permutation(100)
    rare_labels = np.zeros(100, dtype=np.int64)
    rare_labels[[13, 88]] = 1
    rare_scores = np.linspace(.01, .49, 100)
    rare_scores[[13, 88]] = [.8, .4]
    scenarios = (
        MetricScenario("100 peças: matriz", labels[order], scores[order]),
        MetricScenario("8 peças: limiar", np.array([1, 1, 1, 1, 0, 0, 0, 0]),
                       np.array([.9, .7, .45, .3, .6, .35, .32, .1])),
        MetricScenario("Classes raras: 2 em 100", rare_labels, rare_scores),
    )
    for scenario in scenarios:
        scenario.labels.setflags(write=False)
        scenario.scores.setflags(write=False)
    return scenarios
