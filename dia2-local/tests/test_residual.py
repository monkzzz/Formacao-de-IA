import unittest
from pathlib import Path

import numpy as np
import torch

from digitlab.captcha import TRAIN_FONTS, HELDOUT_FONTS
from digitlab.ensemble_benchmark import DEV_FONTS as OLD_DEV, TEST_FONTS as OLD_TEST
from digitlab.highres import EXTRA_FONTS, HighResCNN
from digitlab.residual import ADDED_FONTS, DEV_FONTS, TEST_FONTS, ResidualCNN, make_raw


class ResidualTests(unittest.TestCase):
    def test_identity_initialization_preserves_baseline_and_learns_residual(self):
        torch.set_num_threads(2)
        baseline, model = HighResCNN(), ResidualCNN()
        model.load_state_dict(baseline.state_dict(), strict=False)
        baseline.eval()
        model.eval()
        x = torch.rand(2, 1, 64, 64)
        torch.testing.assert_close(model(x), baseline(x), rtol=0, atol=0)
        first, second, hidden = model.features(x)
        self.assertEqual(tuple(first.shape), (2, 16, 32, 32))
        self.assertEqual(tuple(second.shape), (2, 32, 8, 8))
        self.assertEqual(tuple(hidden.shape), (2, 128))
        torch.nn.functional.cross_entropy(model(x), torch.tensor([2, 9])).backward()
        for p in model.parameters():
            self.assertTrue(torch.isfinite(p.grad).all())
        self.assertGreater(float(model.block1.expand.weight.grad.abs().sum()), 0)
        self.assertGreater(float(model.block2.expand.weight.grad.abs().sum()), 0)

    def test_new_split_names_exclude_all_previous_heldout_families(self):
        train = set(TRAIN_FONTS + EXTRA_FONTS + ADDED_FONTS)
        dev, test = set(DEV_FONTS), set(TEST_FONTS)
        previous = set(HELDOUT_FONTS + OLD_DEV + OLD_TEST)
        self.assertFalse(train & (dev | test | previous))
        self.assertFalse(dev & (test | previous))
        self.assertFalse(test & previous)

    def test_raw_mixture_reproducibility_and_source_isolation(self):
        font = Path("C:/Windows/Fonts/arial.ttf")
        if not font.exists():
            self.skipTest("Font fixture unavailable")
        images = np.zeros((2, 28, 28), np.uint8)
        images[:, 4:24, 12:16] = 255
        labels = np.array([1, 7])
        args = (images, labels, np.array([1]), [font], 40, 67)
        first, second = make_raw(*args), make_raw(*args)
        for a, b in zip(first, second):
            np.testing.assert_array_equal(a, b)
        x, y = first
        self.assertEqual(tuple(x.shape), (40, 1, 64, 64))
        self.assertTrue(torch.isfinite(x).all())
        self.assertTrue((y[1::2] == 7).all())
        np.testing.assert_array_equal(np.bincount(y[::2].numpy()), np.full(10, 2))
