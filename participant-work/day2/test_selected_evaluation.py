"""Focused tests for evaluation aggregation and checkpoint/export integrity."""

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

SPEC = importlib.util.spec_from_file_location("selected_eval", Path(__file__).with_name("verify-selected-evaluation.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SelectedEvaluationTests(unittest.TestCase):
    def test_export_mutation_is_detected(self):
        model = torch.nn.Linear(2, 2)
        tensors, arrays, offset = [], [], 0
        for name, value in model.state_dict().items():
            array = value.detach().numpy().astype("<f4").ravel()
            tensors.append({"name": name, "shape": list(value.shape), "offset": offset, "length": len(array)})
            arrays.append(array)
            offset += len(array)
        blob = np.concatenate(arrays).tobytes()
        manifest = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob), "tensors": tensors}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "weights.bin"
            path.write_bytes(blob)
            MODULE.verify_checkpoint_export(model, manifest, path)
            with torch.no_grad():
                model.weight[0, 0] += 1
            with self.assertRaises(AssertionError):
                MODULE.verify_checkpoint_export(model, manifest, path)
            path.write_bytes(blob + b"bad")
            with self.assertRaisesRegex(ValueError, "manifest"):
                MODULE.verify_checkpoint_export(model, manifest, path)

    def test_metrics_do_not_depend_on_batch_boundaries(self):
        class FixtureModel(torch.nn.Module):
            def forward(self, inputs):
                mass = inputs.sum((1, 2, 3)) / 100
                return mass[:, None] * torch.arange(10)[None, :]

        images = np.zeros((3, 28, 28), dtype=np.uint8)
        images[:, 6:22, 12:16] = 255
        labels = np.array([9, 1, 9], dtype=np.uint8)
        first, predictions = MODULE.evaluate(FixtureModel(), images, labels, batch_size=1)
        second, combined = MODULE.evaluate(FixtureModel(), images, labels, batch_size=3)
        self.assertEqual(first["confusion_matrix"], second["confusion_matrix"])
        self.assertEqual(first["correct"], 2)
        self.assertEqual(first["count"], 3)
        self.assertAlmostEqual(first["loss"], second["loss"], places=5)
        self.assertEqual([p["predicted"] for p in predictions], [p["predicted"] for p in combined])


if __name__ == "__main__":
    unittest.main()
