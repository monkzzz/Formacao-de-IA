"""Restore hash-pinned release weights and verify all public deployment assets."""

import argparse
import hashlib
import json
from pathlib import PurePosixPath
from urllib.request import Request, urlopen

from .ftp_deploy import ROOT, deployment_files
from .qa_outputs import qa_report

PUBLIC_URL = "https://naoquerosaber.pt/AI/"


def download(relative):
    request = Request(PUBLIC_URL + relative, headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def restore_weights():
    metadata = json.loads((ROOT / "deployment-files.json").read_text())
    restored = []
    for name in metadata["files"]:
        if not name.endswith("/weights.bin"):
            continue
        # Validate the path before either reading or creating files.
        relative = PurePosixPath(name)
        if (relative.is_absolute() or ".." in relative.parts or "\\" in name
                or ":" in name or relative.parts[0] != "model"
                or relative.as_posix() != name):
            raise ValueError("Unsafe release weight path")
        path = ROOT / "dist" / name
        if path.is_symlink() or not path.resolve().is_relative_to((ROOT / "dist").resolve()):
            raise ValueError("Unsafe release weight destination")
        manifest = json.loads(path.with_name("manifest.json").read_text())
        data = path.read_bytes() if path.exists() else download(name)
        if len(data) != manifest["bytes"] or hashlib.sha256(data).hexdigest() != manifest["sha256"]:
            raise ValueError("Release weights differ from reviewed manifest: " + name)
        if not path.exists():
            with path.open("xb") as stream:
                stream.write(data)
            restored.append(name)
    deployment_files()  # Validate the complete allowlist before any upload.
    return restored


def verify_http():
    results = []
    for path in deployment_files():
        name = path.relative_to(ROOT / "dist").as_posix()
        actual = hashlib.sha256(download(name)).hexdigest()
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Public asset hash mismatch: " + name)
        results.append({"file": name, "sha256": actual})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", action="store_true")
    parser.add_argument("--verify-http", action="store_true")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report = {"checks": {}, "public_url": PUBLIC_URL}
    with qa_report(ROOT / "reports" / args.report, report):
        if args.restore:
            report["checks"]["restored_weights"] = restore_weights()
        report["checks"]["allowlisted_files"] = len(deployment_files())
        if args.verify_http:
            report["checks"]["public_assets"] = verify_http()
    print(json.dumps({"status": "PASS", "report": args.report}))


if __name__ == "__main__":
    main()
