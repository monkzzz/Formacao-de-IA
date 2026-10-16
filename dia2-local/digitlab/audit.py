"""Check local completion evidence without changing the frozen evaluation."""

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone

import numpy as np

from .train import ROOT, write_json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reports = ROOT / "reports"
    read = lambda name: json.loads((reports / name).read_text(encoding="utf-8"))
    freeze, raw, comparison = read("challenge-freeze.json"), read("challenge-raw.json"), read("challenge-comparison.json")
    test, training, qa = read("mnist-test.json"), read("training.json"), read("browser-qa.json")
    checks = {}
    for name, expected in freeze["sources"].items():
        if name == "digitlab/challenge.py":
            assert digest(ROOT / name) == raw["collector_sha256"]
        else:
            assert digest(ROOT / name) == expected, f"Frozen source changed: {name}"
    checks["frozen_inference_unchanged"] = "PASS; collector repair separately identified"
    assert digest(ROOT / "dist/model/weights.bin") == freeze["model_sha256"]
    assert digest(ROOT / freeze["archive"]) == freeze["archive_sha256"]
    with zipfile.ZipFile(ROOT / freeze["archive"]) as archive:
        for name in archive.namelist():
            assert archive.read(name) == (ROOT / "dist" / name).read_bytes(), name
    checks["frozen_archive_matches_current_app"] = "PASS"
    assert digest(reports / "challenge-freeze.json") == raw["freeze_sha256"]
    assert digest(reports / "challenge-raw.json") == comparison["raw_sha256"]
    assert (datetime.fromisoformat(freeze["frozen_at"]) < datetime.fromisoformat(raw["exported_at"])
            < datetime.fromisoformat(comparison["compared_at"]))
    checks["preserved_record_and_ordering"] = "PASS"
    assert len(raw["predictions"]) == 10 and len(comparison["cases"]) == 10
    assert comparison["correct"] == sum(c["correct"] for c in comparison["cases"]) == 2
    for record in raw["predictions"]:
        assert len(record["scores"]) == 10 and abs(sum(record["scores"]) - 1) < 1e-12
        assert int(np.argmax(record["scores"])) == record["predicted"]
        assert len(record["input"]) == 784
        assert hashlib.sha256(np.asarray(record["input"], dtype="<f4").tobytes()).hexdigest() == record["input_sha256"]
        assert digest(ROOT.parent / "Dia2/Desafio" / record["file"]) == record["file_sha256"]
    checks["challenge_pixels_scores_and_comparison"] = "PASS"
    matrix = np.asarray(test["confusion_matrix"])
    assert matrix.shape == (10, 10) and matrix.sum() == test["count"] == 10000
    assert matrix.trace() == test["correct"] == 9928
    assert len(test["error_indices"]) == 72
    assert len(training["history"]) == 18
    selected = min(training["history"], key=lambda r: r["validation"]["loss"])
    assert selected["epoch"] == test["selected_epoch"] == training["selected_epoch"]
    assert all(check["status"] == "PASS" for check in qa["checks"].values())
    checks["mnist_metrics_model_selection_and_browser_evidence"] = "PASS"
    required = ["reports/figures/learning-curves.png", "reports/figures/mnist-confusion.png",
                "reports/figures/challenge-inputs.png", "reports/screenshots/desktop.png",
                "reports/screenshots/mobile.png", "reports/screenshots/challenge-all.png",
                "reports/validation.md", "artifacts/best.pt", "artifacts/split.npz"]
    assert all((ROOT / name).is_file() for name in required)
    broken = []
    for name in ["README.md", "docs/experiment.md", "reports/validation.md"]:
        path = ROOT / name
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" not in link and not (path.parent / link).exists():
                broken.append([name, link])
    assert not broken, broken
    checks["artifacts_figures_and_document_links"] = "PASS"
    audit = {"audited_at": datetime.now(timezone.utc).isoformat(), "scope": "local Desafio implementation",
             "checks": checks, "mnist_correct": 9928, "mnist_count": 10000,
             "challenge_correct": 2, "challenge_count": 10,
             "not_claimed": ["public deployment", "teacher feedback", "all Day 2 exercises completed"]}
    write_json(reports / "completion-audit.json", audit)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
