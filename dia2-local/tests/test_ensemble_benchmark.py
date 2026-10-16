import unittest

import numpy as np

from digitlab.ensemble_benchmark import DEV_FONTS, TEST_FONTS, mix_scores, metrics
from digitlab.captcha import TRAIN_FONTS, HELDOUT_FONTS
from digitlab.highres import EXTRA_FONTS


class EnsembleBenchmarkTests(unittest.TestCase):
    def test_endpoints_and_disagreement_use_scores_without_labels(self):
        low, high = np.zeros((2, 10)), np.zeros((2, 10))
        low[:, 3], low[:, 5] = .6, .4
        high[:, 3], high[:, 5] = .1, .9
        np.testing.assert_array_equal(mix_scores(low, high, 0), low)
        np.testing.assert_array_equal(mix_scores(low, high, 1), high)
        self.assertEqual(mix_scores(low, high, .75).argmax(1).tolist(), [5, 5])
        np.testing.assert_allclose(mix_scores(low, high, .5).sum(1), 1)
        self.assertEqual(metrics(high, np.array([5, 3]))["correct"], 1)
        with self.assertRaises(ValueError):
            mix_scores(low, high, 1.1)
        with self.assertRaises(ValueError):
            mix_scores(low[:, :9], high, .5)

    def test_font_families_are_separate_from_training_and_each_other(self):
        historical = set(TRAIN_FONTS + EXTRA_FONTS + HELDOUT_FONTS)
        self.assertFalse(set(DEV_FONTS) & set(TEST_FONTS))
        self.assertFalse(set(DEV_FONTS + TEST_FONTS) & historical)
