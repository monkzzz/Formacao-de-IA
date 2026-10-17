"""Verified EMNIST Digits extraction and pixel-level split hygiene."""

import gzip
import hashlib
import json
import struct
import zipfile

import numpy as np

from .emnist_data import DIRECTORY as EMNIST, MD5, URL
from .train import ROOT, write_json

DIRECTORY = ROOT / "data/emnist-digits"


def extract(archive=EMNIST / "gzip.zip", destination=DIRECTORY):
    """Reuse the official archive without touching the Letters extraction."""
    with archive.open("rb") as stream:
        if hashlib.file_digest(stream, "md5").hexdigest() != MD5:
            raise ValueError("Official EMNIST archive checksum failed")
    destination.mkdir(parents=True, exist_ok=True)
    hashes = {}
    with zipfile.ZipFile(archive) as bundle:
        for partition in ("train", "test"):
            for kind, dimension in (("images", 3), ("labels", 1)):
                name = f"emnist-digits-{partition}-{kind}-idx{dimension}-ubyte.gz"
                member = next(n for n in bundle.namelist() if n.split("/")[-1] == name)
                data = bundle.read(member)
                target = destination / name
                if target.exists() and target.read_bytes() != data:
                    raise ValueError("Existing Digits extraction changed")
                target.write_bytes(data)
                hashes[name] = hashlib.sha256(data).hexdigest()
    provenance = {"source": URL, "archive_md5": MD5, "sha256": hashes,
                  "orientation": "transpose IDX rows and columns to upright",
                  "attribution": "Cohen, Afshar, Tapson and van Schaik (2017), EMNIST; NIST distribution"}
    write_json(destination / "provenance.json", provenance)
    return provenance


def decode(data, count, images):
    raw = gzip.decompress(data)
    magic = 2051 if images else 2049
    if len(raw) < 8 or struct.unpack(">II", raw[:8]) != (magic, count):
        raise ValueError("Invalid EMNIST Digits header/count")
    if images:
        if len(raw) != 16 + count * 784 or struct.unpack(">II", raw[8:16]) != (28, 28):
            raise ValueError("Invalid EMNIST Digits dimensions/payload")
        return np.frombuffer(raw, np.uint8, offset=16).reshape(count, 28, 28).transpose(0, 2, 1).copy()
    if len(raw) != 8 + count:
        raise ValueError("Invalid EMNIST Digits labels payload")
    labels = np.frombuffer(raw, np.uint8, offset=8).copy()
    if np.any(labels > 9):
        raise ValueError("Invalid EMNIST Digits class")
    return labels


def load_partition(train=True, directory=DIRECTORY):
    partition, count = ("train", 240000) if train else ("test", 40000)
    provenance = json.loads((directory / "provenance.json").read_text())
    result = []
    for kind, dimension in (("images", 3), ("labels", 1)):
        name = f"emnist-digits-{partition}-{kind}-idx{dimension}-ubyte.gz"
        data = (directory / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != provenance["sha256"][name]:
            raise ValueError("EMNIST Digits integrity failure")
        result.append(decode(data, count, kind == "images"))
    return tuple(result)


def fingerprints(images):
    return [hashlib.sha256(image.tobytes()).digest() for image in images]


def unique_indices(images, excluded):
    """Discard exact duplicates, including across labels and reserved partitions."""
    seen = set(excluded)
    kept = []
    for index, fingerprint in enumerate(fingerprints(images)):
        if fingerprint not in seen:
            kept.append(index)
            seen.add(fingerprint)
    return np.asarray(kept, dtype=np.int64)


def stratified_split(labels, indices, validation_per_class=500, seed=2026102001):
    rng = np.random.default_rng(seed)
    train, validation = [], []
    for digit in range(10):
        candidates = rng.permutation(indices[labels[indices] == digit])
        if len(candidates) <= validation_per_class:
            raise ValueError("Insufficient independent supplementary examples")
        validation.extend(candidates[:validation_per_class])
        train.extend(candidates[validation_per_class:])
    return rng.permutation(train), rng.permutation(validation)
