"""Verify the current letter release against its actual artifacts and reports."""

import hashlib
import json
import zipfile
from datetime import datetime, timezone

import numpy as np

from .train import ROOT, write_json


def main():
    read = lambda name: json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))
    metrics, training = read("letters-test.json"), read("letters-training.json")
    matrix = np.asarray(metrics["confusion_matrix"])
    assert matrix.shape == (26, 26) and matrix.sum() == metrics["count"] == 20800
    assert matrix.trace() == metrics["correct"] == 19508
    np.testing.assert_array_equal(matrix.sum(axis=1), np.full(26, 800))
    assert min(training["history"], key=lambda row: row["validation"]["loss"])["epoch"] == metrics["selected_epoch"]
    split = np.load(ROOT / "artifacts/letters/split.npz")
    assert len(split["train"]) == 114400 and len(split["validation"]) == 10400
    assert not np.intersect1d(split["train"], split["validation"]).size
    assert len(np.union1d(split["train"], split["validation"])) == 124800
    groups = {}
    for name in ["letters-browser-qa.json", "digits-browser-qa-v2.json",
                 "public-letters-browser-qa.json", "public-browser-qa-v2.json"]:
        result = read(name)
        assert all(check["status"] == "PASS" for check in result["checks"].values()), name
        groups[name] = len(result["checks"])
    assert groups == {"letters-browser-qa.json": 10, "digits-browser-qa-v2.json": 9,
                      "public-letters-browser-qa.json": 10, "public-browser-qa-v2.json": 9}
    manifests = []
    for directory in [ROOT / "dist/model", ROOT / "dist/model/letters"]:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        assert hashlib.sha256((directory / "weights.bin").read_bytes()).hexdigest() == manifest["sha256"]
        manifests.append(manifest)
    assert manifests[1]["sha256"] == metrics["model_sha256"]
    assert manifests[0]["sha256"] == read("challenge-freeze.json")["model_sha256"]
    assert hashlib.sha256((ROOT / "reports/challenge-raw.json").read_bytes()).hexdigest() == read("challenge-comparison.json")["raw_sha256"]
    deployment = read("ftp-deployment.json")
    assert len(deployment["files"]) == 13
    expected_paths = {path.relative_to(ROOT / "dist").as_posix() for path in (ROOT / "dist").rglob("*")
                      if path.is_file() and path.name != "parity.json"}
    assert {item["file"] for item in deployment["files"]} == expected_paths
    for item in deployment["files"]:
        assert hashlib.sha256((ROOT / "dist" / item["file"]).read_bytes()).hexdigest() == item["sha256"]
        assert not any(part in item["file"] for part in ["ftp.local", "parity.json", "data/emnist"])
    with zipfile.ZipFile(ROOT / "artifacts/digitlab-website-v2.zip") as archive:
        assert set(archive.namelist()) == expected_paths
        for name in archive.namelist():
            assert archive.read(name) == (ROOT / "dist" / name).read_bytes()
    release = {"audited_at": datetime.now(timezone.utc).isoformat(), "scope": "Digits and Letters v2",
               "letters_correct": metrics["correct"], "letters_test_count": metrics["count"],
               "letters_accuracy": metrics["accuracy"], "public_url": "https://naoquerosaber.pt/AI/index.html",
               "qa_groups": groups, "uploaded_assets": len(expected_paths),
               "original_digit_weights_and_challenge_record": "unchanged",
               "weights_match_manifests": True, "package_matches_deployed_assets": True,
               "credentials_and_training_data_in_package": False}
    write_json(ROOT / "reports/letters-completion-audit.json", release)
    print(json.dumps(release, indent=2))


if __name__ == "__main__":
    main()
