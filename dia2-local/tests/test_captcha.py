"""Guard synthetic data independence, class balance and image contracts."""

from pathlib import Path
import unittest

import numpy as np

from digitlab.captcha import HELDOUT_FONTS, TRAIN_FONTS, make_raw, render
from digitlab.preprocess import prepare


class CaptchaTests(unittest.TestCase):
    def test_raw_images_are_reproducible_and_valid_for_both_polarities(self):
        source = np.zeros((28, 28), np.uint8)
        source[4:24, 12:16] = 255
        for seed in range(25):
            a = np.asarray(render(np.random.default_rng(seed), 1, source=source))
            b = np.asarray(render(np.random.default_rng(seed), 1, source=source))
            np.testing.assert_array_equal(a, b)
            result = prepare(a)
            self.assertEqual(result.shape, (1, 28, 28))
            self.assertTrue(np.isfinite(result).all())
            self.assertGreater(float(result.sum()), 0)

    def test_printed_classes_are_balanced_and_mnist_uses_supplied_indices(self):
        font = Path(__file__).resolve().parents[1] / "data/open-fonts/lato/Lato-Regular.ttf"
        if not font.exists():
            self.skipTest("Run python ../setup_course.py --fonts to obtain the portable font fixture")
        images = np.zeros((2, 28, 28), np.uint8)
        images[:, 4:24, 12:16] = 255
        labels = np.array([1, 7])
        x, y = make_raw(images, labels, np.array([1]), [font], 40, 9)
        np.testing.assert_array_equal(np.bincount(y[::2].numpy()), np.full(10, 2))
        self.assertTrue((y[1::2] == 7).all())
        self.assertEqual(tuple(x.shape), (40, 1, 28, 28))
        self.assertFalse(set(TRAIN_FONTS) & set(HELDOUT_FONTS))


if __name__ == "__main__":
    unittest.main()
