"""Download official EMNIST with canonical integrity checks and upright images."""

import gzip
import hashlib
import json
import struct
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
URL = "https://biometrics.nist.gov/cs_links/EMNIST/gzip.zip"
MD5 = "58c8d27c78d21e728a6bc7b3cc06412e"  # Official torchvision EMNIST archive checksum.
DIRECTORY = ROOT / "data/emnist"


def download():
    """Verify the complete official archive before extracting only Letters files."""
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    archive = DIRECTORY / "gzip.zip"
    if not archive.exists():
        part = archive.with_suffix(".zip.part")
        request = urllib.request.Request(URL, headers={"User-Agent": "DigitLab-EMNIST/1.0"})
        print("Downloading official NIST EMNIST archive...", flush=True)
        with urllib.request.urlopen(request, timeout=60) as response, part.open("wb") as output:
            total, reported = 0, 0
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                total += len(chunk)
                if total - reported >= 32 * 1024 * 1024:
                    reported = total
                    print(f"Downloaded {total / 1024**2:.0f} MiB", flush=True)
        part.rename(archive)
    with archive.open("rb") as handle:
        if hashlib.file_digest(handle, "md5").hexdigest() != MD5:
            raise ValueError("Official EMNIST archive checksum failed; do not use this download")
    names = [f"emnist-letters-{partition}-{kind}-idx{dimension}-ubyte.gz"
             for partition in ["train", "test"]
             for kind, dimension in [("images", 3), ("labels", 1)]]
    hashes = {}
    with zipfile.ZipFile(archive) as bundle:
        for name in names + ["emnist-letters-mapping.txt"]:
            member = next(n for n in bundle.namelist() if n.split("/")[-1] == name)
            data = bundle.read(member)
            (DIRECTORY / name).write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
    (DIRECTORY / "provenance.json").write_text(json.dumps({"source": URL, "archive_md5": MD5,
        "sha256": hashes, "orientation": "transpose raw IDX rows/columns to upright handwriting",
        "classes": "labels 1–26 mapped to uppercase A–Z; lowercase and uppercase forms share a class"}, indent=2), encoding="utf-8")
    print("Canonical archive verified; Letters files extracted.", flush=True)


def load_partition(train=True):
    """Load all original Letters examples; reject malformed or modified files."""
    partition, count = ("train", 124800) if train else ("test", 20800)
    provenance = json.loads((DIRECTORY / "provenance.json").read_text(encoding="utf-8"))
    arrays = []
    for kind, dimension in [("images", 3), ("labels", 1)]:
        name = f"emnist-letters-{partition}-{kind}-idx{dimension}-ubyte.gz"
        data = (DIRECTORY / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != provenance["sha256"][name]:
            raise ValueError(f"EMNIST integrity failure: {name}")
        raw = gzip.decompress(data)
        if struct.unpack(">II", raw[:8]) != (2051 if kind == "images" else 2049, count):
            raise ValueError("Unexpected EMNIST header/count")
        if kind == "images":
            if struct.unpack(">II", raw[8:16]) != (28, 28) or len(raw) != 16 + count * 784:
                raise ValueError("Unexpected EMNIST image dimensions/payload")
            # The original EMNIST storage axes are transposed relative to an upright glyph.
            images = np.frombuffer(raw, np.uint8, offset=16).reshape(count, 28, 28)
            arrays.append(images.transpose(0, 2, 1).copy())
        else:
            if len(raw) != 8 + count:
                raise ValueError("Unexpected EMNIST label payload")
            labels = np.frombuffer(raw, np.uint8, offset=8).astype(np.int64) - 1
            if labels.min() != 0 or labels.max() != 25:
                raise ValueError("Unexpected EMNIST label range")
            arrays.append(labels)
    return tuple(arrays)


if __name__ == "__main__":
    download()
