"""Meaningful contract, leakage and gradient checks; no challenge inputs."""

import hashlib
import json
import unittest
from pathlib import Path

import numpy as np
import torch

from digitlab.data import load_partition, split_indices
from digitlab.model import DigitCNN
from digitlab.preprocess import prepare

ROOT = Path(__file__).resolve().parents[1]


class PreprocessingTests(unittest.TestCase):
    def test_blank_and_transparent_inputs_are_rejected(self):
        for color in [0, 255]:
            image = np.full((35, 50, 4), color, dtype=np.uint8)
            image[:, :, 3] = 255
            with self.assertRaises(ValueError):
                prepare(image)
        with self.assertRaises(ValueError):
            prepare(np.zeros((40, 40, 4), dtype=np.uint8))

    def test_polarity_translation_and_centering(self):
        image = np.zeros((70, 90, 4), dtype=np.uint8)
        image[:, :, 3] = 255
        image[10:45, 15:24, :3] = 255
        image[36:45, 15:40, :3] = 255
        inverse = image.copy()
        inverse[:, :, :3] = 255 - inverse[:, :, :3]
        translated = np.zeros_like(image)
        translated[:, :, 3] = 255
        translated[20:55, 35:44, :3] = 255
        translated[46:55, 35:60, :3] = 255
        result = prepare(image)
        np.testing.assert_allclose(result, prepare(inverse), atol=1e-6)
        np.testing.assert_allclose(result, prepare(translated), atol=1e-6)
        self.assertEqual(result.shape, (1, 28, 28))
        self.assertTrue(np.isfinite(result).all())
        self.assertGreater(result.sum(), 1)
        yy, xx = np.indices((28, 28))
        self.assertLess(abs(float((result[0] * xx).sum() / result.sum()) - 13.5), .51)
        self.assertLess(abs(float((result[0] * yy).sum() / result.sum()) - 13.5), .51)


class ModelTests(unittest.TestCase):
    def test_dimensions_and_finite_gradients(self):
        torch.manual_seed(17)
        model = DigitCNN()
        x = torch.rand(3, 1, 28, 28)
        output = model(x)
        self.assertEqual(tuple(output.shape), (3, 10))
        torch.nn.functional.cross_entropy(output, torch.tensor([0, 4, 9])).backward()
        for parameter in model.parameters():
            self.assertIsNotNone(parameter.grad)
            self.assertTrue(torch.isfinite(parameter.grad).all())

    def test_model_can_learn_a_small_training_fixture(self):
        torch.manual_seed(2)
        torch.set_num_threads(2)
        model = DigitCNN().train()
        x = torch.zeros(8, 1, 28, 28)
        x[:4, :, 3:10, 3:10] = 1
        x[4:, :, 18:25, 18:25] = 1
        y = torch.tensor([0] * 4 + [1] * 4)
        optimizer = torch.optim.Adam(model.parameters(), lr=.005)
        for _ in range(35):
            optimizer.zero_grad()
            loss = torch.nn.functional.cross_entropy(model(x), y)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            self.assertEqual(int((model(x).argmax(1) == y).sum()), 8)


class DataTests(unittest.TestCase):
    def test_real_mnist_split_is_reproducible_stratified_and_disjoint(self):
        images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
        self.assertEqual(images.shape, (60000, 28, 28))
        train, validation = split_indices(labels)
        train_again, validation_again = split_indices(labels)
        np.testing.assert_array_equal(train, train_again)
        np.testing.assert_array_equal(validation, validation_again)
        self.assertEqual(len(train), 55000)
        self.assertEqual(len(validation), 5000)
        self.assertEqual(len(np.intersect1d(train, validation)), 0)
        self.assertEqual(len(np.union1d(train, validation)), 60000)
        np.testing.assert_array_equal(np.bincount(labels[validation]), np.full(10, 500))

    def test_export_integrity_if_present(self):
        path = ROOT / "dist/model/manifest.json"
        if not path.exists():
            self.skipTest("Export not created yet")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        blob = (path.parent / "weights.bin").read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), manifest["sha256"])
        self.assertEqual(len(blob), manifest["bytes"])
        self.assertEqual(sum(t["length"] for t in manifest["tensors"]) * 4, len(blob))


if __name__ == "__main__":
    unittest.main()
