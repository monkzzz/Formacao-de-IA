"""Check data isolation, annotated preprocessing, consistency and capacity claims."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch

from digitlab.confidence_data import CONDITIONS, make_set, trace_crop
from digitlab.confidence_suite import choose_arm, consistency_loss, make_model
import digitlab.confidence_suite as suite
from digitlab.residual import ResidualCNN


class ConsistencySuiteTests(unittest.TestCase):
    def test_corruption_cells_are_balanced_reproducible_and_source_isolated(self):
        font = Path(__file__).resolve().parents[1] / "data/open-fonts/lato/Lato-Regular.ttf"
        if not font.exists():
            self.skipTest("Run setup_course.py --fonts")
        images = np.zeros((20, 28, 28), np.uint8)
        images[:, 5:23, 10:17] = 255
        labels = np.arange(20) % 10
        indices = np.arange(10, 20)
        args = (images, labels, indices, [font], 120, 319)
        first, second = make_set(*args, annotations=True), make_set(*args, annotations=True)
        torch.testing.assert_close(first["views"], second["views"], rtol=0, atol=0)
        self.assertTrue(torch.isfinite(first["views"]).all())
        self.assertTrue(((first["views"] >= 0) & (first["views"] <= 1)).all())
        for condition in CONDITIONS:
            for printed in (True, False):
                chosen = (first["conditions"] == condition) & (first["printed"] == printed)
                np.testing.assert_array_equal(np.bincount(first["labels"][chosen].numpy()), np.ones(10))
        for row in first["records"]:
            if not row["printed"]:
                self.assertIn(row["source_index"], indices)
                self.assertEqual(labels[row["source_index"]], row["label"])
        clean = first["conditions"] == "clean"
        torch.testing.assert_close(first["views"][clean, 0], first["views"][clean, 2], rtol=0, atol=0)

    def test_annotations_detect_noise_driven_shrinkage_without_losing_crop_coverage(self):
        mask = np.zeros((128, 128), np.uint8)
        mask[35:95, 55:70] = 255
        clean = np.full((128, 128, 4), 255, np.uint8)
        clean[mask > 0, :3] = 0
        noisy = clean.copy()
        noisy[3, 3, :3] = noisy[124, 124, :3] = 0
        a = trace_crop(Image.fromarray(clean), Image.fromarray(mask))
        b = trace_crop(Image.fromarray(noisy), Image.fromarray(mask))
        self.assertEqual(a["glyph_long_side_after_resize"], 48)
        self.assertLess(b["glyph_long_side_after_resize"], 24)
        self.assertEqual(b["crop_glyph_mass_retained"], 1)
        self.assertGreater(b["crop_area_over_glyph_box"], a["crop_area_over_glyph_box"])

    def test_consistency_is_zero_for_matching_views_shift_invariant_and_differentiable(self):
        logits = torch.randn(4, 1, 10).repeat(1, 3, 1)
        self.assertLess(abs(consistency_loss(logits).item()), 1e-6)
        logits[:, 1, 0] += 5
        logits.requires_grad_()
        loss = consistency_loss(logits)
        self.assertGreater(loss.item(), 0)
        torch.testing.assert_close(loss, consistency_loss(logits + 100), atol=1e-6, rtol=1e-5)
        loss.backward()
        self.assertTrue(torch.isfinite(logits.grad).all())
        self.assertGreater(logits.grad.abs().sum().item(), 0)

    def test_capacity_starts_identically_and_additional_blocks_receive_gradients(self):
        torch.set_num_threads(2)
        baseline = ResidualCNN().eval()
        model = make_model("capacity", baseline.state_dict()).eval()
        x = torch.rand(2, 1, 64, 64)
        torch.testing.assert_close(model(x), baseline(x), rtol=0, atol=0)
        self.assertGreater(sum(p.numel() for p in model.parameters()), sum(p.numel() for p in baseline.parameters()))
        torch.nn.functional.cross_entropy(model(x), torch.tensor([2, 9])).backward()
        self.assertGreater(model.block3.expand.weight.grad.abs().sum().item(), 0)
        self.assertGreater(model.block4.expand.weight.grad.abs().sum().item(), 0)

    def test_capacity_requires_meaningful_increment_and_never_selects_rejected_arms(self):
        def result(loss, accuracy=.98, coverage=.95):
            return {"selected_epoch": 1, "validation": {"raw": {
                "loss": loss, "accuracy": accuracy, "correct_at_90_fraction": coverage}}}
        arms = {"control": result(.1), "consistency": result(.09), "capacity": result(.089)}
        self.assertEqual(choose_arm(arms), "consistency")
        arms["capacity"] = result(.08)
        self.assertEqual(choose_arm(arms), "capacity")
        arms["capacity"] = result(.08, coverage=.94)
        self.assertEqual(choose_arm(arms), "consistency")
        arms = {name: {} for name in arms}
        self.assertIsNone(choose_arm(arms))

    def test_final_data_are_not_loaded_when_browser_gate_fails_or_test_is_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "reports").mkdir()
            (root / "reports" / (suite.NAME + "-browser.json")).write_text(json.dumps({"status": "FAIL"}))
            for metadata in ({}, {"test": {"historical": True}}):
                with patch.object(suite, "ROOT", root), patch.object(suite, "DIRECTORY", root / "artifacts"), \
                        patch.object(suite, "load_selection", return_value=(metadata, {}, None)), \
                        patch.object(suite, "load_partition") as loader:
                    with self.assertRaises(ValueError):
                        suite.final_test()
                    loader.assert_not_called()
                self.assertFalse((root / "artifacts/test-started.json").exists())


if __name__ == "__main__":
    unittest.main()
