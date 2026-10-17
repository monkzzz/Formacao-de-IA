import copy
import unittest

import numpy as np

from digitlab.preprocess import prepare
from digitlab.preprocessing_variants import VARIANTS, fit_foreground, foreground, prepare_variant, remove_small
from digitlab.preprocessing_study import qualifies


class PreprocessingStudyTests(unittest.TestCase):
    def test_shared_fit_matches_production_for_colored_alpha_and_non_square_inputs(self):
        rng = np.random.default_rng(27)
        for side in (28, 64):
            for width, height in ((49, 73), (55, 37)):
                rgba = rng.integers(0, 256, (height, width, 4), dtype=np.uint8)
                rgba[[0, -1], :, :3] = 240
                rgba[:, [0, -1], :3] = 240
                for index in (0, 1, 2):
                    rgba[10:25, 12:25, index] = 20
                np.testing.assert_array_equal(fit_foreground(foreground(rgba), side), prepare(rgba, side))
                np.testing.assert_array_equal(prepare_variant(rgba, "current", side), prepare(rgba, side))

    def test_component_filter_removes_small_speck_but_preserves_large_disconnected_strokes(self):
        ink = np.zeros((80, 80))
        ink[15:65, 25:35] = 1
        ink[40:50, 45:55] = 1
        ink[2, 2] = 1
        clean = remove_small(ink)
        self.assertEqual(clean[2, 2], 0)
        self.assertEqual(clean[40:50, 45:55].sum(), 100)
        self.assertEqual(ink[2, 2], 1)

    def test_blank_inputs_fail_every_variant(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                prepare_variant(np.full((50, 50, 4), 255, np.uint8), variant)

    def test_coverage_gain_does_not_excuse_confident_errors_or_clean_regression(self):
        baseline = {"raw": {"accuracy": .98, "correct_above_90_fraction": .90,
                            "loss": .08, "brier": .02, "ece_10_bins": .01, "wrong_above_90_count": 2},
                    "clean": {"accuracy": .99}}
        candidate = copy.deepcopy(baseline)
        candidate["raw"].update(correct_above_90_fraction=.91, loss=.07)
        self.assertTrue(qualifies(candidate, baseline))
        candidate["raw"]["wrong_above_90_count"] = 3
        self.assertFalse(qualifies(candidate, baseline))
        candidate["raw"]["wrong_above_90_count"] = 2
        candidate["clean"]["accuracy"] = .988
        self.assertFalse(qualifies(candidate, baseline))
        candidate["clean"]["accuracy"] = .99
        candidate["preprocessing_failures"] = 1
        self.assertFalse(qualifies(candidate, baseline))
