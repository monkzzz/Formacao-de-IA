"""Verify and assemble the frozen participant-trained ZIP for GitHub Pages."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "dia2-local/reports/self-trained-submission-cleanup-v4-build.json"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def build(archive, output):
    receipt = json.loads(RECEIPT.read_text())
    archive, output = Path(archive).resolve(), Path(output).resolve()
    if output.exists() or output == ROOT or output in ROOT.parents or ROOT / "dia2-local/dist" in output.parents:
        raise ValueError("Use a new separate artifact directory")
    if sha(archive.read_bytes()) != receipt["archive_sha256"]:
        raise ValueError("Submission archive hash differs from reviewed build")
    expected = receipt["files_sha256"]
    with zipfile.ZipFile(archive) as bundle:
        if set(bundle.namelist()) != set(expected) or len(bundle.namelist()) != len(expected):
            raise ValueError("Unexpected or duplicate submission files")
        payloads = {}
        for name, value in expected.items():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise ValueError("Unsafe archive entry")
            if bundle.getinfo(name).file_size > 20 * 1024 * 1024:
                raise ValueError("Oversized archive entry")
            blob = bundle.read(name)
            if sha(blob) != value:
                raise ValueError("Submission asset identity mismatch: " + name)
            payloads[name] = blob
    for folder in ("model", "model/mnist-supplementary-v1/digits", "model/captcha-v3/digits", "model/robust/letters"):
        manifest = json.loads(payloads[folder + "/manifest.json"])
        weights = payloads[folder + "/weights.bin"]
        if sha(weights) != manifest["sha256"] or len(weights) != manifest["bytes"]:
            raise ValueError("Model manifest/weights mismatch")
    output.mkdir(parents=True)
    for name, blob in payloads.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    build = {"scope": "Reviewed participant-trained submission only; no pretrained readers, datasets, credentials or ROMs",
             "submission": receipt["name"], "archive_sha256": receipt["archive_sha256"],
             "receipt_sha256": sha(RECEIPT.read_bytes()), "asset_sha256": expected,
             "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
             "official_captcha_inference": "NOT RUN", "original_external_website_modified": False}
    (output / "pages-build.json").write_text(json.dumps(build, indent=2) + "\n")
    print(f"PASS: {len(expected)} frozen assets and four participant-trained weight exports verified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.archive, args.output)
