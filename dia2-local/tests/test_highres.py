import unittest
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from digitlab.highres import EXTRA_FONTS, HighResCNN, make_raw
from digitlab.captcha import TRAIN_FONTS, HELDOUT_FONTS
from digitlab.model import DigitCNN
from digitlab.preprocess import prepare
from digitlab.train import ROOT


class HighResolutionTests(unittest.TestCase):
    def test_broad_raw_generator_is_balanced_reproducible_and_uses_only_supplied_indices(self):
        font = Path("C:/Windows/Fonts/arial.ttf")
        if not font.exists():
            self.skipTest("Windows font fixture unavailable")
        images = np.zeros((2, 28, 28), np.uint8)
        images[:, 4:24, 12:16] = 255
        labels = np.array([1, 7])
        first = make_raw(images, labels, np.array([1]), [font], 40, 91)
        second = make_raw(images, labels, np.array([1]), [font], 40, 91)
        for a, b in zip(first, second):
            np.testing.assert_array_equal(a, b)
        high, low, targets = first
        self.assertEqual(tuple(high.shape), (40, 1, 64, 64))
        self.assertEqual(tuple(low.shape), (40, 1, 28, 28))
        self.assertTrue(torch.isfinite(high).all() and torch.isfinite(low).all())
        self.assertTrue((targets[1::2] == 7).all())
        np.testing.assert_array_equal(np.bincount(targets[::2].numpy()), np.full(10, 2))
        self.assertFalse(set(TRAIN_FONTS + EXTRA_FONTS) & set(HELDOUT_FONTS))

    def test_legacy_pixels_match_original_non_challenge_fixtures(self):
        path = ROOT / "dist/model/parity.json"
        if not path.exists() or not (ROOT / "reports/mnist-fixtures/digit-0.png").exists():
            self.skipTest("Original non-challenge fixtures unavailable")
        cases = json.loads(path.read_text())["cases"]
        for digit, case in enumerate(cases):
            image = np.asarray(Image.open(ROOT / f"reports/mnist-fixtures/digit-{digit}.png").convert("RGBA"))
            np.testing.assert_array_equal(prepare(image).flatten(), case["input"])

    def test_both_input_contracts_keep_polarity_center_and_reject_blank(self):
        image = np.full((90, 100, 4), 255, np.uint8)
        image[12:70, 30:42, :3] = 0
        image[58:70, 30:67, :3] = 0
        inverse = image.copy()
        inverse[:, :, :3] = 255 - inverse[:, :, :3]
        for side in (28, 64):
            prepared = prepare(image, side)
            np.testing.assert_array_equal(prepared, prepare(inverse, side))
            self.assertEqual(prepared.shape, (1, side, side))
            yy, xx = np.indices((side, side))
            for coordinate in (yy, xx):
                self.assertLess(abs(float((prepared[0] * coordinate).sum() / prepared.sum()) - (side - 1) / 2), .51)
            with self.assertRaises(ValueError):
                prepare(np.full_like(image, 255), side)
        with self.assertRaises(ValueError):
            prepare(image, 32)

    def test_transferred_network_has_real_feature_shapes_and_finite_gradients(self):
        torch.set_num_threads(2)
        model = HighResCNN()
        model.initialize_from(DigitCNN().state_dict())
        x = torch.rand(2, 1, 64, 64)
        first, second, hidden = model.features(x)
        self.assertEqual(tuple(first.shape), (2, 16, 32, 32))
        self.assertEqual(tuple(second.shape), (2, 32, 8, 8))
        self.assertEqual(tuple(hidden.shape), (2, 128))
        torch.nn.functional.cross_entropy(model(x), torch.tensor([0, 9])).backward()
        self.assertTrue(all(torch.isfinite(p.grad).all() for p in model.parameters()))
