"""Check confidence diagnostics and rejection of misleading score increases."""

import copy
import unittest

import numpy as np

from digitlab.confidence import eligible, score_metrics


class ConfidenceTests(unittest.TestCase):
    def test_correct_and_wrong_high_confidence_are_distinct(self):
        scores = np.full((3, 10), .01)
        scores[0, 0] = scores[1, 1] = .91
        scores[2] = .1
        metrics = score_metrics(scores, [0, 0, 2])
        self.assertEqual(metrics["correct_at_90_count"], 1)
        self.assertEqual(metrics["wrong_at_90_count"], 1)
        self.assertAlmostEqual(metrics["accuracy_when_score_at_least_90"], .5)
        self.assertEqual(sum(map(sum, metrics["confusion_matrix"])), 3)

    def test_gate_rejects_confidence_gain_with_worse_proper_scores(self):
        baseline = {"raw": {"accuracy": .99, "loss": .03, "brier": .01,
                            "ece_10_bins": .01, "correct_at_90_fraction": .95},
                    "clean": {"accuracy": .99}}
        candidate = copy.deepcopy(baseline)
        candidate["raw"].update(correct_at_90_fraction=.97, loss=.04)
        self.assertFalse(eligible(candidate, baseline))
        candidate["raw"]["loss"] = .02
        self.assertTrue(eligible(candidate, baseline))


if __name__ == "__main__":
    unittest.main()
