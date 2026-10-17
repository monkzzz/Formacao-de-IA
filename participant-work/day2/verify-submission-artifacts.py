"""Restore release weights in a new stdlib-only environment; preserve originals."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dia2-local"
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=HERE / "submission-artifact-verification.json")
    destination = parser.parse_args().report.resolve()
    if destination.exists():
        raise SystemExit("Preserve existing evidence; choose a new report destination.")
    workspace = APP / ".tmp" / ("submission-" + uuid.uuid4().hex)
    workspace.mkdir(parents=True)
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(),
              "status": "FAIL", "scope": "Clean stdlib-only venv, copied server and manifests, real HTTPS downloads",
              "models": [], "limitations": ["Restores browser weights, not training checkpoints or optional pretrained readers",
                                             "No training, accuracy evaluation, browser QA or deployment performed"]}
    originals = {}
    for experiment, mode in (("captcha-v3", "digits"), ("robust", "letters")):
        relative = Path("model") / experiment / mode
        source = APP / "dist" / relative
        target = workspace / "dist" / relative
        target.mkdir(parents=True)
        shutil.copy2(source / "manifest.json", target / "manifest.json")
        originals[str(relative)] = digest(source / "weights.bin")
    shutil.copy2(APP / "serve.py", workspace / "serve.py")
    try:
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(workspace / "venv")], check=True)
        python = workspace / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        code = "from pathlib import Path; from serve import prepare_models; prepare_models(Path('dist'), download=True)"
        run = subprocess.run([str(python), "-I", "-c",
                              "import sys; sys.path.insert(0, '.'); " + code],
                             cwd=workspace, capture_output=True, text=True, timeout=150)
        record.update(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr)
        run.check_returncode()
        for relative, original_hash in originals.items():
            folder = workspace / "dist" / relative
            manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
            restored = folder / "weights.bin"
            actual = digest(restored)
            unchanged = digest(APP / "dist" / relative / "weights.bin") == original_hash
            assert actual == manifest["sha256"] == original_hash and unchanged
            assert restored.stat().st_size == manifest["bytes"]
            record["models"].append({"path": relative, "sha256": actual,
                                     "bytes": restored.stat().st_size, "original_unchanged": unchanged})
        record["status"] = "PASS"
    finally:
        destination.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
