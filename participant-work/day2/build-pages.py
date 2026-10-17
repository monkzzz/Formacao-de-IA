"""Assemble a separate Pages artifact from tracked static assets and verified weights."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "dia2-local/dist"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output == ROOT or SOURCE in output.parents or output in SOURCE.parents:
        parser.error("Use a new separate output directory")
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "dia2-local/dist"], cwd=ROOT
    ).decode().split("\0")
    output.mkdir(parents=True)
    for name in filter(None, tracked):
        source = ROOT / name
        relative = source.relative_to(SOURCE)
        if source.is_symlink() or source.suffix in (".bin", ".sfc", ".pt", ".pth"):
            raise ValueError(f"Unexpected tracked binary or symlink: {name}")
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    models = []
    for path in sorted((output / "model").rglob("manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        relative = path.parent.relative_to(output) / "weights.bin"
        url = "https://naoquerosaber.pt/AI/" + relative.as_posix()
        with urlopen(url, timeout=90) as response:
            data = response.read(manifest["bytes"] + 1)
        actual = hashlib.sha256(data).hexdigest()
        if len(data) != manifest["bytes"] or actual != manifest["sha256"]:
            raise ValueError(f"Weight identity mismatch: {relative}")
        (output / relative).write_bytes(data)
        models.append({"path": relative.as_posix(), "bytes": len(data), "sha256": actual, "source": url})
    (output / ".nojekyll").touch()
    files = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(output.rglob("*")) if p.is_file()}
    receipt = {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "models": models, "asset_sha256": files,
               "scope": "Separate static deployment; no ROM/checkpoint/dataset/credential publication; external optional OCR unchanged"}
    (output / "pages-build.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(files)} assets, {len(models)} verified weight files; original dist untouched")


if __name__ == "__main__":
    main()
