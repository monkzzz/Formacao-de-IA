"""Source/contrast balance and strict refusal controls for the combined study."""

from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from digitlab.balanced_color import gates, test as reserved_test
from digitlab.balanced_color_data import make_raw, palette


class BalancedColorTests(unittest.TestCase):
    def test_palette_constraints(self):
        rng = np.random.default_rng(42)
        for isoluminant in (False, True):
            for _ in range(40):
                a, b = palette(rng, isoluminant)
                difference = abs((a - b) @ np.array([.299, .587, .114]))
                self.assertGreaterEqual(np.sqrt(np.mean((a - b) ** 2)), 80)
                if isoluminant:
                    self.assertLessEqual(difference, .057001)
                else:
                    self.assertGreaterEqual(difference, 60)

    def test_balanced_deterministic_views_and_rejections(self):
        pixels = np.full((64, 64, 4), 255, np.uint8)
        pixels[8:55, 25:36, :3] = 0
        images = np.zeros((10, 28, 28), np.uint8)
        labels = np.arange(10)
        with patch("digitlab.balanced_color_data.render", return_value=Image.fromarray(pixels)):
            a, records = make_raw(images, labels, np.arange(10), [Path("unused.ttf")], 60, 42)
            b, _ = make_raw(images, labels, np.arange(10), [Path("unused.ttf")], 60, 42)
        np.testing.assert_array_equal(a["rgb"], b["rgb"])
        self.assertEqual(int(a["gray_rejected"].sum()), 20)
        cells = {(r["label"], r["printed"], r["kind"]) for r in records}
        self.assertEqual(len(cells), 60)
        self.assertTrue(all(r["source_index"] is None or labels[r["source_index"]] == r["label"] for r in records))

    def test_strict_gain_bridge_and_confident_error_gates(self):
        def result(count):
            return {"raw": {"count": 1800, "accuracy": .98, "correct_above_90_count": count,
                            "loss": .1 if count == 1700 else .09, "brier": .03, "ece_10_bins": .01,
                            "wrong_above_90_count": 2, "rejected": 0},
                    "legacy": {"accuracy": .98}, "clean": {"accuracy": .99, "rejected": 0},
                    "bridge": {"accuracy": .98, "rejected": 0}}
        base, candidate = result(1700), result(1709)
        self.assertTrue(all(gates(candidate, base).values()))
        candidate["raw"]["correct_above_90_count"] = 1708
        self.assertFalse(gates(candidate, base)["strict_90_gain"])
        candidate["bridge"]["accuracy"] = .978
        self.assertFalse(gates(candidate, base)["bridge_accuracy"])
        candidate["raw"]["wrong_above_90_count"] = 3
        self.assertFalse(gates(candidate, base)["confident_errors"])

    def test_no_selected_pair_cannot_load_reserved_sources(self):
        with patch("digitlab.balanced_color.selected", side_effect=ValueError("No eligible development pair")), patch("digitlab.balanced_color.load_partition") as load:
            with self.assertRaisesRegex(ValueError, "No eligible"):
                reserved_test()
            load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
