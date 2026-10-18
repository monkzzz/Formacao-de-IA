"""RGB contrast must recover chromatic ink without changing neutral glyphs."""

import unittest

import numpy as np

from digitlab.color_preprocess import prepare_color
from digitlab.color_study import metrics
from digitlab.preprocess import prepare


def glyph(background, ink):
    pixels = np.empty((40, 32, 4), np.uint8)
    pixels[:] = (*background, 255)
    pixels[7:34, 14:19] = (*ink, 255)
    pixels[7:12, 9:19] = (*ink, 255)
    return pixels


class ColorPreprocessTests(unittest.TestCase):
    def test_isoluminant_ink_and_polarity(self):
        for b, f in (((220, 40, 40), (40, 100, 203)), ((40, 100, 203), (220, 40, 40))):
            pixels = glyph(b, f)
            with self.assertRaises(ValueError):
                prepare(pixels)
            actual = prepare_color(pixels)
            self.assertGreater(float(actual.sum()), 100)
            np.testing.assert_allclose(actual, prepare_color(glyph((255, 255, 255), (0, 0, 0))), atol=1e-6)

    def test_neutral_contract_and_alpha(self):
        for side in (28, 64):
            for b, f in (((255,)*3, (0,)*3), ((0,)*3, (255,)*3)):
                image = glyph(b, f)
                np.testing.assert_allclose(prepare_color(image, side), prepare(image, side), atol=1e-6)
            image = glyph((255,)*3, (0,)*3)
            transparent = image.copy()
            transparent[image[:, :, 0] == 255] = (200, 10, 230, 0)
            np.testing.assert_allclose(prepare_color(image, side), prepare_color(transparent, side), atol=1e-6)

    def test_reject_blank_low_contrast_and_invalid_input(self):
        for image in (glyph((100,)*3, (100,)*3), glyph((100,)*3, (110,)*3), np.zeros((1, 4, 4), np.uint8)):
            with self.assertRaises(ValueError):
                prepare_color(image)
        with self.assertRaises(ValueError):
            prepare_color(glyph((255,)*3, (0,)*3), 32)

    def test_rejection_never_counts_as_digit_zero(self):
        scores = np.array([[.1]*10, [.91]+[.01]*9, [.9]+[.1/9]*9])
        measured = metrics(scores, np.array([0, 0, 0]), np.array([True, False, False]))
        self.assertEqual(measured["correct"], 2)
        self.assertEqual(measured["rejected"], 1)
        self.assertEqual(measured["correct_above_90_count"], 1)
        self.assertEqual(measured["confusion_matrix_with_rejection"][0][10], 1)


if __name__ == "__main__":
    unittest.main()
