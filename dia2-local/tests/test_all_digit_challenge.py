import unittest
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from digitlab.all_digit_challenge import compare_rows
from digitlab import all_digit_challenge


class ChallengeComparisonTests(unittest.TestCase):
    def test_cli_selects_release_and_relocated_artifacts_without_recording(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(all_digit_challenge.__dict__, {}):
            root = Path(temporary)
            arguments = ["all_digit_challenge", "--stage", "freeze", "--name", "new-release",
                         "--build", str(root / "receipt.json"), "--site", str(root / "site"),
                         "--archive", str(root / "archive.zip"), "--report-root", str(root / "reports"),
                         "--snapshot-root", str(root / "snapshots")]
            with patch.object(sys, "argv", arguments), patch.object(all_digit_challenge, "freeze_runtime") as freeze:
                all_digit_challenge.main()
                freeze.assert_called_once()
                self.assertEqual(all_digit_challenge.NAME, "new-release")
                self.assertEqual(all_digit_challenge.BUILD, root / "receipt.json")
                self.assertEqual(all_digit_challenge.ARTIFACT_OPTIONS["site"], root / "site")
                self.assertEqual(all_digit_challenge.SNAPSHOT_ROOT, root / "snapshots")

    def setUp(self):
        self.expected = {f"case-{i}": i for i in range(10)}

    def test_ocr_rejections_remain_wrong_without_invented_scores(self):
        rows = [{"file": name, "predicted": value, "scores": None} for name, value in self.expected.items()]
        rows[0].update(predicted=None, raw_text="O")
        result = compare_rows(rows, self.expected)
        self.assertEqual(result["correct"], 9)
        self.assertIsNone(result["correct_above_90"])
        self.assertIsNone(result["score_target_met"])
        self.assertEqual(result["cases"][0]["raw_text"], "O")

    def test_exact_ninety_fails_strict_target(self):
        rows = []
        for name, value in self.expected.items():
            scores = [.1 / 9] * 10
            scores[value] = .9
            rows.append({"file": name, "predicted": value, "scores": scores})
        result = compare_rows(rows, self.expected)
        self.assertEqual(result["correct"], 10)
        self.assertEqual(result["correct_above_90"], 0)
        self.assertFalse(result["score_target_met"])

    def test_incomplete_or_duplicate_cases_are_rejected(self):
        rows = [{"file": name, "predicted": value, "scores": None} for name, value in self.expected.items()]
        with self.assertRaises(ValueError):
            compare_rows(rows[:-1], self.expected)
        rows[-1] = rows[0]
        with self.assertRaises(ValueError):
            compare_rows(rows, self.expected)

    def test_inference_failure_is_not_scored_as_prediction(self):
        rows = [{"file": name, "predicted": value, "scores": None} for name, value in self.expected.items()]
        rows[0]["error"] = "Download failed"
        with self.assertRaises(ValueError):
            compare_rows(rows, self.expected)

    def test_mixed_score_availability_is_rejected(self):
        rows = [{"file": name, "predicted": value, "scores": None} for name, value in self.expected.items()]
        rows[0]["scores"] = [.1] * 10
        with self.assertRaises(ValueError):
            compare_rows(rows, self.expected)


if __name__ == "__main__":
    unittest.main()
