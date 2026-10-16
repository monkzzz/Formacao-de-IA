"""Read-only verification of deployed static bytes and JavaScript MIME types."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from urllib.parse import quote
from urllib.request import urlopen

from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://naoquerosaber.pt/AI/")
    parser.add_argument("--report", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--experiment", default="captcha-v2")
    args = parser.parse_args()
    target = ROOT / "reports" / args.report
    if target.exists():
        parser.error("Use a new report destination to preserve evidence")
    base = args.url.rstrip("/") + "/"

    def check(path):
        relative = path.relative_to(ROOT / "dist").as_posix()
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        with urlopen(base + quote(relative) + "?verify=" + quote(args.version), timeout=60) as response:
            data = response.read()
            mime = response.headers.get_content_type()
        actual = hashlib.sha256(data).hexdigest()
        status = "PASS" if actual == expected and (path.suffix != ".js" or mime in
                    ("text/javascript", "application/javascript")) else "FAIL"
        return {"file": relative, "bytes": len(data), "sha256": actual,
                "expected_sha256": expected, "mime": mime, "status": status}

    paths = sorted(path for path in (ROOT / "dist").rglob("*") if path.is_file() and path.name != "parity.json")
    with ThreadPoolExecutor(max_workers=4) as pool:
        files = list(pool.map(check, paths))
    freeze = json.loads((ROOT / "reports" / (args.experiment + "-challenge-freeze.json")).read_text())
    changed = [name for name, digest in freeze["sources"].items()
               if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    status = "PASS" if not changed and all(row["status"] == "PASS" for row in files) else "FAIL"
    write_json(target, {"status": status, "url": base, "application_version": args.version,
                        "count": len(files), "frozen_sources_unchanged": not changed,
                        "changed_frozen_sources": changed, "files": files})
    print(f"{status}: {len(files)} HTTPS assets, JavaScript MIME types and frozen-source integrity")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
