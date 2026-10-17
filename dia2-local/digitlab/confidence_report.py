"""Validate rejected confidence experiments and preservation without new inference."""

from datetime import datetime, timezone
import json
import re
import runpy
import subprocess
from pathlib import Path
from urllib.parse import unquote

from .confidence import digest
from .train import ROOT, write_json


def main():
    destination = ROOT / "reports/captcha-confidence-validation.json"
    assert not destination.exists(), "Preserve prior validation"
    records = {}
    for name, epochs in [("captcha-confidence-v1", 8), ("captcha-confidence-head-v1", 16)]:
        path = ROOT / "reports" / (name + ".json")
        record = json.loads(path.read_text())
        assert len(record["history"]) == epochs
        assert record["status"] == "RETAIN BASELINE; no eligible epoch"
        assert not any(row["eligible"] for row in record["history"])
        assert "test" not in record and "selected_epoch" not in record
        directory = ROOT / "artifacts" / name
        assert (directory / "last.pt").exists() and not (directory / "best.pt").exists()
        assert not (directory / "test-started.json").exists()
        assert digest(ROOT / "artifacts/captcha-v3/best.pt") == record["baseline_checkpoint_sha256"]
        source_hashes = record["source_sha256"]
        if isinstance(source_hashes, dict):
            assert all(digest(ROOT / "digitlab" / n) == value for n, value in source_hashes.items())
        else:
            assert digest(ROOT / "digitlab/confidence_head.py") == source_hashes
            assert digest(ROOT / "digitlab/confidence.py") == record["shared_gate_source_sha256"]
        records[name] = {"status": record["status"], "epochs": epochs, "report_sha256": digest(path),
                         "last_checkpoint_sha256": digest(directory / "last.pt"),
                         "final_development": {kind: record["history"][-1][kind] for kind in ["clean", "raw"]}}
    repository = ROOT.parent
    protection = json.loads((repository / "participant-work/day2/submission-challenge-integrity.json").read_text())
    for name, value in protection["historical_report_hashes"].items():
        assert digest(ROOT / "reports" / name) == value
    old = json.loads((repository / "participant-work/day2/selected-mnist-clean-reevaluation.json").read_text())
    for name, value in old["preserved_sha256_before"].items():
        assert digest(repository / name) == value
    assert not subprocess.check_output(["rtk", "proxy", "git", "diff", "1e649c3", "--", "dia2-local/dist"], cwd=repository)
    anchors = runpy.run_path(str(repository / "participant-work/day2/validate-independent-completion.py"))["anchors"]
    links = 0
    for path in [repository / "TASKS.md", ROOT / "docs/confidence-experiment.md"]:
        for raw in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if raw.startswith(("http:", "https:", "mailto:")):
                continue
            target, _, fragment = unquote(raw).partition("#")
            resolved = (path.parent / target).resolve() if target else path
            assert resolved.exists() or resolved == destination, raw
            if fragment:
                assert fragment in anchors(resolved), raw
            links += 1
    result = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "target_achieved": False, "active_model_retained": True, "experiments": records,
              "historical_models_exports_and_reports_unchanged": True,
              "deployment": "NOT RUN: neither candidate qualified",
              "fresh_test_browser_and_official_followup": "NOT RUN: no eligible development selection",
              "relative_links_checked": links,
              "unit_tests_executed_in_this_batch": {"command": ".venv/Scripts/python.exe -m unittest discover -s tests -v",
                                                    "tests": 32, "result": "PASS", "seconds": 5.642,
                                                    "timing": "Earlier in this batch; subsequent head training completed with frozen-feature identity assertion"},
              "teacher_feedback_status": "Participant-reported criterion; no witnessed teacher session or acceptance"}
    write_json(destination, result)
    print(f"PASS: two completed rejected experiments, preserved baseline, {links} links; teacher target NOT achieved")


if __name__ == "__main__":
    main()
