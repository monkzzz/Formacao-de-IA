"""Recover the residual checkpoint from verified browser tensors, without training."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from .residual import ARCHITECTURE, ResidualCNN
from .train import ROOT


def restore(folder, output):
    if output.exists():
        raise FileExistsError(f"Preserve existing checkpoint: {output}")
    manifest = json.loads((folder / "manifest.json").read_text())
    data = (folder / "weights.bin").read_bytes()
    if (manifest["architecture"] != ARCHITECTURE or manifest["dtype"] != "float32-le"
            or len(data) != manifest["bytes"]
            or hashlib.sha256(data).hexdigest() != manifest["sha256"]):
        raise ValueError("Browser weights do not match the residual manifest")
    expected = ResidualCNN().state_dict()
    state, cursor = {}, 0
    for item in manifest["tensors"]:
        name = item["name"]
        shape = tuple(item["shape"])
        length = item["length"]
        if (name not in expected or name in state or shape != tuple(expected[name].shape)
                or item["offset"] != cursor or length != expected[name].numel()):
            raise ValueError("Invalid exported tensor layout")
        state[name] = torch.from_numpy(np.frombuffer(data, dtype="<f4", count=length,
                                                   offset=cursor * 4).copy().reshape(shape))
        cursor += length
    if set(state) != set(expected) or cursor * 4 != len(data):
        raise ValueError("Incomplete exported tensor layout")
    model = ResidualCNN()
    model.load_state_dict(state)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        torch.save(model.state_dict(), stream)
    return {"status": "PASS", "output": str(output), "tensor_export_sha256": manifest["sha256"],
            "checkpoint_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "scope": "Exact tensor recovery; serialized checkpoint hash may differ from original"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights-dir", type=Path, default=ROOT / "dist/model/captcha-v3/digits")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/captcha-v3/best.pt")
    args = parser.parse_args()
    print(json.dumps(restore(args.weights_dir, args.output), indent=2))


if __name__ == "__main__":
    main()
