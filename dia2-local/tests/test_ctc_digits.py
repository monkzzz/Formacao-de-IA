import unittest

import numpy as np
import torch

from digitlab.ctc_digits import digit_log_probabilities, digit_scores


class CTCDigitTests(unittest.TestCase):
    def test_single_character_likelihood_matches_pytorch_ctc_loss(self):
        charset = ["", *"0123456789", "X"]
        logits = np.random.default_rng(703).normal(size=(7, len(charset)))
        expected = []
        log_probs = torch.tensor(logits, dtype=torch.float64).log_softmax(-1)[:, None, :]
        for index in range(1, 11):
            loss = torch.nn.functional.ctc_loss(log_probs, torch.tensor([index]), torch.tensor([7]),
                torch.tensor([1]), blank=0, reduction="none")
            expected.append(-loss.item())
        np.testing.assert_allclose(digit_log_probabilities(logits, charset), expected, atol=1e-10)

    def test_vocabulary_competitors_and_per_frame_offsets_do_not_change_conditional_scores(self):
        charset = ["", *"0123456789", "X"]
        logits = np.random.default_rng(705).normal(size=(8, len(charset)))
        expected = digit_scores(logits, charset)
        altered = logits + np.arange(8)[:, None] * 100
        altered[:, -1] += 250
        np.testing.assert_allclose(digit_scores(altered, charset), expected, atol=1e-12)
        self.assertAlmostEqual(float(expected.sum()), 1)
        self.assertTrue(np.isfinite(expected).all())
