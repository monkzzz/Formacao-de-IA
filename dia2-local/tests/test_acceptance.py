import copy
import json
import unittest

import numpy as np

from digitlab.acceptance import evaluate


class ProfessorAcceptanceTests(unittest.TestCase):
    def records(self, score):
        records, expected = [], {}
        for digit in range(10):
            name = f"independent-{digit}.png"
            scores = [(1 - score) / 9] * 10
            scores[digit] = score
            records.append({"file": name, "predicted": digit, "scores": scores})
            expected[name] = digit
        return records, expected

    def test_exactly_ninety_fails_but_a_strictly_higher_raw_score_passes(self):
        records, expected = self.records(.9)
        result = evaluate(records, expected)
        self.assertEqual(result["correct"], 10)
        self.assertEqual(result["correct_above_90"], 0)
        self.assertFalse(result["accepted"])
        records, expected = self.records(float(np.nextafter(.9, 1.)))
        result = json.loads(json.dumps(evaluate(records, expected)))
        self.assertEqual(result["correct_above_90"], 10)
        self.assertTrue(result["accepted"])

    def test_one_confident_error_or_one_uncertain_correct_case_fails(self):
        records, expected = self.records(.95)
        wrong = copy.deepcopy(expected)
        wrong["independent-0.png"] = 1
        self.assertFalse(evaluate(records, wrong)["accepted"])
        uncertain, _ = self.records(.8)
        records[0] = uncertain[0]
        result = evaluate(records, expected)
        self.assertEqual(result["correct"], 10)
        self.assertEqual(result["correct_above_90"], 9)
        self.assertFalse(result["accepted"])

    def test_missing_or_duplicate_cases_are_rejected(self):
        records, expected = self.records(.95)
        with self.assertRaises(ValueError):
            evaluate(records[:-1], expected)
        records[-1] = records[0]
        with self.assertRaises(ValueError):
            evaluate(records, expected)
