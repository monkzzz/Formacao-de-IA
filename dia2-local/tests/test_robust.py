"""Check augmentation reproducibility and validation promotion safeguards."""

import unittest

import torch

from digitlab.robust import distort, noisy_copy, qualifies


class RobustnessTests(unittest.TestCase):
    def test_corruptions_are_reproducible_finite_and_do_not_modify_inputs(self):
        x = torch.zeros(32, 1, 28, 28)
        x[:, :, 5:23, 12:16] = 1
        original = x.clone()
        torch.manual_seed(71)
        first = distort(x)
        torch.manual_seed(71)
        second = distort(x)
        self.assertTrue(torch.equal(first, second))
        self.assertTrue(torch.equal(x, original))
        self.assertEqual(first.shape, x.shape)
        self.assertTrue(torch.isfinite(first).all())
        self.assertGreaterEqual(float(first.min()), 0)
        self.assertLessEqual(float(first.max()), 1)
        self.assertGreater(float((first - x).abs().mean()), .01)
        self.assertTrue((first.sum((1, 2, 3)) > 1).all())

    def test_fixed_evaluation_noise_does_not_change_training_random_stream(self):
        x = torch.zeros(8, 1, 28, 28)
        x[:, :, 5:22, 10:15] = 1
        torch.manual_seed(123)
        before = torch.random.get_rng_state()
        first = noisy_copy(x, 77)
        self.assertTrue(torch.equal(before, torch.random.get_rng_state()))
        self.assertTrue(torch.equal(first, noisy_copy(x, 77)))
        self.assertFalse(torch.equal(first, noisy_copy(x, 78)))

    def test_candidate_must_improve_noise_without_exceeding_clean_loss_limit(self):
        baseline = {"clean": {"accuracy": .99}, "noisy": {"accuracy": .90}}
        self.assertTrue(qualifies(baseline, {"accuracy": .989}, {"accuracy": .93}, .002))
        self.assertFalse(qualifies(baseline, {"accuracy": .98}, {"accuracy": .99}, .002))
        self.assertFalse(qualifies(baseline, {"accuracy": .995}, {"accuracy": .90}, .002))


if __name__ == "__main__":
    unittest.main()
