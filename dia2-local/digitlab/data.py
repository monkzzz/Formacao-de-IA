"""Strict loader for the four original MNIST IDX gzip files."""

import gzip
import hashlib
import struct
from pathlib import Path

import numpy as np

FILES = {
    "train-images-idx3-ubyte.gz": (2051, 60000, "f68b3c2dcbeaaa9fbdd348bbdeb94873"),
    "train-labels-idx1-ubyte.gz": (2049, 60000, "d53e105ee54ea40749a09fcbcd1e9432"),
    "t10k-images-idx3-ubyte.gz": (2051, 10000, "9fb629c4189551a2d022fa330f9573f3"),
    "t10k-labels-idx1-ubyte.gz": (2049, 10000, "ec29112dd5afa0611ce80d1b7f02629c"),
}


def load_file(path: Path) -> np.ndarray:
    """Verify canonical checksum, header and exact payload length."""
    magic, count, checksum = FILES[path.name]
    blob = path.read_bytes()
    if hashlib.md5(blob).hexdigest() != checksum:
        raise ValueError(f"MNIST checksum mismatch: {path.name}")
    raw = gzip.decompress(blob)
    actual_magic, actual_count = struct.unpack(">II", raw[:8])
    if (actual_magic, actual_count) != (magic, count):
        raise ValueError(f"Invalid IDX header: {path.name}")
    if magic == 2051:
        if struct.unpack(">II", raw[8:16]) != (28, 28) or len(raw) != 16 + count * 784:
            raise ValueError(f"Invalid image dimensions or payload: {path.name}")
        return np.frombuffer(raw, dtype=np.uint8, offset=16).reshape(count, 28, 28).copy()
    if len(raw) != 8 + count:
        raise ValueError(f"Invalid label payload: {path.name}")
    labels = np.frombuffer(raw, dtype=np.uint8, offset=8).copy()
    if np.any(labels > 9):
        raise ValueError("MNIST label outside 0–9")
    return labels


def load_partition(directory: Path, train: bool) -> tuple[np.ndarray, np.ndarray]:
    prefix = "train" if train else "t10k"
    return (load_file(directory / f"{prefix}-images-idx3-ubyte.gz"),
            load_file(directory / f"{prefix}-labels-idx1-ubyte.gz"))


def split_indices(labels: np.ndarray, seed: int = 20261016) -> tuple[np.ndarray, np.ndarray]:
    """Reserve exactly 500 examples of each class for validation."""
    rng = np.random.default_rng(seed)
    train, validation = [], []
    for digit in range(10):
        indices = rng.permutation(np.flatnonzero(labels == digit))
        validation.extend(indices[:500])
        train.extend(indices[500:])
    return rng.permutation(train), rng.permutation(validation)
