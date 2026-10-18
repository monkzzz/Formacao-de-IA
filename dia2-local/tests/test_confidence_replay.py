import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch

from digitlab.confidence_replay import qualifies, replay_loss
from digitlab import confidence_replay


class ConfidenceReplayTests(unittest.TestCase):
    def test_rejected_selection_refuses_before_loading_reserved_samples(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "report.json"
            report.write_text("{}")
            (root / "selection.json").write_text(json.dumps({"selected_epoch": None}))
            with patch.object(confidence_replay, "DIRECTORY", root), patch.object(confidence_replay, "REPORT", report), \
                    patch.object(confidence_replay, "load_partition") as load:
                with self.assertRaisesRegex(ValueError, "remain unopened"):
                    confidence_replay.test()
                load.assert_not_called()

    def test_retention_loss_handles_no_correct_teacher_and_backpropagates(self):
        logits = torch.zeros(2, 10, requires_grad=True)
        teacher = torch.zeros(2, 10)
        teacher[:, 1] = 1
        loss = replay_loss(logits, torch.zeros(2, dtype=torch.long), teacher)
        self.assertTrue(torch.isfinite(loss))
        loss.backward()
        self.assertTrue(torch.isfinite(logits.grad).all())

    def test_better_confidence_cannot_hide_accuracy_or_bridge_regression(self):
        raw = {"accuracy": .99, "correct_above_90_fraction": .95, "loss": .05,
               "brier": .02, "ece_10_bins": .01, "wrong_above_90": 1}
        baseline = {"raw": raw, "clean": {"accuracy": .99}, "bridge": {"accuracy": .99}}
        candidate = copy.deepcopy(baseline)
        candidate["raw"].update(correct_above_90_fraction=.96, loss=.04)
        self.assertTrue(qualifies(candidate, baseline))
        candidate["bridge"]["accuracy"] = .98
        self.assertFalse(qualifies(candidate, baseline))
        candidate["bridge"]["accuracy"] = .99
        candidate["raw"]["wrong_above_90"] = 2
        self.assertFalse(qualifies(candidate, baseline))
