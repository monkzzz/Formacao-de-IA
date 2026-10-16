"""Verify a design-only release without replacing historical model evidence."""

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone

from .train import ROOT, write_json


def main():
    read = lambda name: json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))
    reports = {name: read(name) for name in ["design-qa.json", "design-digits-qa.json", "design-letters-qa.json",
                "public-design-qa.json", "public-design-digits-qa.json", "public-design-letters-qa.json"]}
    for name, report in reports.items():
        assert all(check["status"] == "PASS" for check in report["checks"].values()), name
    assert sum(len(r["checks"]) for name, r in reports.items() if name.startswith("public-")) == 25
    assert sum(len(r["checks"]) for name, r in reports.items() if not name.startswith("public-")) == 25
    for mode, expected in [("", read("challenge-freeze.json")["model_sha256"]),
                           ("letters", read("letters-test.json")["model_sha256"])]:
        assert hashlib.sha256((ROOT / "dist/model" / mode / "weights.bin").read_bytes()).hexdigest() == expected
    for name in ["inference.js", "preprocess.js"]:
        assert (ROOT / "dist/v3" / name).read_bytes() == (ROOT / "dist/v2" / name).read_bytes()
    assert hashlib.sha256((ROOT / "reports/challenge-raw.json").read_bytes()).hexdigest() == read("challenge-comparison.json")["raw_sha256"]
    deployment = read("ftp-deployment.json")
    assert len(deployment["files"]) == 17
    paths = {p.relative_to(ROOT / "dist").as_posix() for p in (ROOT / "dist").rglob("*")
             if p.is_file() and p.name != "parity.json"}
    assert paths == {item["file"] for item in deployment["files"]}
    for item in deployment["files"]:
        assert hashlib.sha256((ROOT / "dist" / item["file"]).read_bytes()).hexdigest() == item["sha256"]
    with zipfile.ZipFile(ROOT / "artifacts/digitlab-website-v3.zip") as archive:
        assert set(archive.namelist()) == paths
        for name in archive.namelist():
            assert archive.read(name) == (ROOT / "dist" / name).read_bytes()
    for filename in ["README.md", "docs/hosting.md", "reports/design-validation.md"]:
        path = ROOT / filename
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            assert "://" in link or (path.parent / link).exists(), (filename, link)
    audit = {"audited_at": datetime.now(timezone.utc).isoformat(), "release": "website design v3",
             "public_url": "https://naoquerosaber.pt/AI/index.html", "local_qa_groups": 25, "public_qa_groups": 25,
             "model_weights_preprocessing_and_inference": "unchanged", "original_challenge_record": "unchanged",
             "verified_assets": len(paths), "reports_and_package": "PASS"}
    write_json(ROOT / "reports/design-completion-audit.json", audit)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
