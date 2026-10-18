"""Submission verification must reject changed bytes and unrelated checkpoints."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import torch

from digitlab.self_trained_submission import verified_weights


class SelfTrainedSubmissionTests(unittest.TestCase):
    def test_verifies_export_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = {"weight": torch.tensor([[1., 2.]])}
            blob = state["weight"].numpy().astype("<f4").tobytes()
            manifest = {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
                        "tensors": [{"name": "weight", "shape": [1, 2], "length": 2, "offset": 0}]}
            (root / "manifest.json").write_text(json.dumps(manifest))
            (root / "weights.bin").write_bytes(blob)
            torch.save(state, root / "local.pt")
            self.assertEqual(verified_weights(root, root / "local.pt")["sha256"], manifest["sha256"])
            (root / "weights.bin").write_bytes(bytes(len(blob)))
            with self.assertRaisesRegex(ValueError, "integrity"):
                verified_weights(root, root / "local.pt")

    def test_valid_export_rejects_different_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blob = torch.tensor([1.]).numpy().astype("<f4").tobytes()
            manifest = {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
                        "tensors": [{"name": "weight", "shape": [1], "length": 1, "offset": 0}]}
            (root / "manifest.json").write_text(json.dumps(manifest))
            (root / "weights.bin").write_bytes(blob)
            torch.save({"weight": torch.tensor([2.])}, root / "unrelated.pt")
            with self.assertRaisesRegex(ValueError, "local checkpoint"):
                verified_weights(root, root / "unrelated.pt")


if __name__ == "__main__":
    unittest.main()
