"""Recover every exported tensor and reject corruption or existing destinations."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import torch

from digitlab.residual import ARCHITECTURE, ResidualCNN
from digitlab.restore_checkpoint import restore


class RestoreCheckpointTests(unittest.TestCase):
    def test_exact_roundtrip_corruption_rejection_and_preservation(self):
        state = ResidualCNN().state_dict()
        tensors, chunks, cursor = [], [], 0
        for name, tensor in state.items():
            chunks.append(tensor.numpy().astype("<f4").tobytes())
            tensors.append({"name": name, "shape": list(tensor.shape), "offset": cursor,
                            "length": tensor.numel()})
            cursor += tensor.numel()
        data = b"".join(chunks)
        manifest = {"architecture": ARCHITECTURE, "dtype": "float32-le", "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(), "tensors": tensors}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "manifest.json").write_text(json.dumps(manifest))
            (folder / "weights.bin").write_bytes(data)
            output = folder / "recovered.pt"
            restore(folder, output)
            recovered = torch.load(output, map_location="cpu", weights_only=True)
            for name in state:
                torch.testing.assert_close(state[name], recovered[name], rtol=0, atol=0)
            before = output.read_bytes()
            with self.assertRaises(FileExistsError):
                restore(folder, output)
            self.assertEqual(output.read_bytes(), before)
            (folder / "weights.bin").write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, "do not match"):
                restore(folder, folder / "corrupt.pt")
            self.assertFalse((folder / "corrupt.pt").exists())


if __name__ == "__main__":
    unittest.main()
