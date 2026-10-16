"""Letter-specific label, orientation, separation and model checks."""

import unittest

import numpy as np
import torch

from digitlab.emnist_data import DIRECTORY, load_partition
from digitlab.letters import LABELS, LetterCNN, split_indices


class LetterTests(unittest.TestCase):
    def test_output_classes_and_gradients(self):
        model = LetterCNN()
        output = model(torch.rand(2, 1, 28, 28))
        self.assertEqual(tuple(output.shape), (2, 26))
        self.assertEqual("".join(LABELS), "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        torch.nn.functional.cross_entropy(output, torch.tensor([0, 25])).backward()
        for parameter in model.parameters():
            self.assertTrue(torch.isfinite(parameter.grad).all())

    @unittest.skipUnless((DIRECTORY / "provenance.json").exists(), "Official EMNIST not downloaded")
    def test_full_training_partition_and_class_balanced_validation(self):
        images, labels = load_partition(True)
        self.assertEqual(images.shape, (124800, 28, 28))
        np.testing.assert_array_equal(np.bincount(labels), np.full(26, 4800))
        train, validation = split_indices(labels)
        second_train, second_validation = split_indices(labels)
        self.assertEqual(len(train), 114400)
        self.assertEqual(len(validation), 10400)
        self.assertEqual(len(np.intersect1d(train, validation)), 0)
        self.assertEqual(len(np.union1d(train, validation)), 124800)
        np.testing.assert_array_equal(train, second_train)
        np.testing.assert_array_equal(validation, second_validation)
        np.testing.assert_array_equal(np.bincount(labels[validation]), np.full(26, 400))


if __name__ == "__main__":
    unittest.main()
