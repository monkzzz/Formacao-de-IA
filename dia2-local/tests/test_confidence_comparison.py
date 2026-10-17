"""Post-freeze score comparison never equates confident errors with success."""

import copy
import json
import unittest

from digitlab.confidence_suite_browser import compare_predictions


class ConfidenceComparisonTests(unittest.TestCase):
    def test_confident_error_and_uncertain_correct_prediction_fail_target(self):
        records = [{"file": "independent-a.png", "predicted": 0, "scores": [.91] + [.01] * 9},
                   {"file": "independent-b.png", "predicted": 1, "scores": [.01, .91] + [.01] * 8}]
        expected = {"independent-a.png": 0, "independent-b.png": 1}
        result = compare_predictions(records, expected)
        self.assertTrue(result["target_met"])
        self.assertEqual(result["correct_at_90"], 2)
        self.assertEqual(json.loads(json.dumps(result))["correct_at_90"], 2)
        wrong = dict(expected, **{"independent-b.png": 0})
        result = compare_predictions(records, wrong)
        self.assertFalse(result["target_met"])
        self.assertEqual(result["correct_at_90"], 1)
        uncertain = copy.deepcopy(records)
        uncertain[1]["scores"] = [.025, .775] + [.025] * 8
        result = compare_predictions(uncertain, expected)
        self.assertFalse(result["target_met"])
        self.assertEqual(result["correct"], 2)

    def test_duplicate_missing_and_inconsistent_predictions_are_rejected(self):
        row = {"file": "independent.png", "predicted": 0, "scores": [.91] + [.01] * 9}
        for records, expected in (([row, row], {"independent.png": 0}),
                                  ([row], {"different.png": 0}),
                                  ([dict(row, predicted=1)], {"independent.png": 0})):
            with self.assertRaises(ValueError):
                compare_predictions(records, expected)


if __name__ == "__main__":
    unittest.main()
