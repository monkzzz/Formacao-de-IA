"""Validate the final local handover, preserving prior execution evidence."""

import ast
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def anchors(path):
    content = path.read_text(encoding="utf-8")
    result = set(re.findall(r'(?:id|name)=["\']([^"\']+)', content))
    counts = Counter()
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", content, re.MULTILINE):
        plain = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        result.add(plain + (f"-{counts[plain]}" if counts[plain] else ""))
        counts[plain] += 1
    return result


def main():
    destination = Path(__file__).with_name("handover-validation.json")
    if destination.exists():
        raise SystemExit("Evidence exists; choose a new destination")
    documents = ["README.md", "TASKS.md", "PREPARATION.md", "SLIDE-REVIEW.md", "SUBMISSION.md",
                 "participant-work/starter/context/handoff.md", "participant-work/day2/teaching-assets-review.md",
                 "participant-work/day2/teacher-feedback-packet.md", "participant-work/day2/handover-completion.md"]
    links = fragment_count = 0
    for name in documents:
        path = ROOT / name
        for raw in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if raw.startswith(("https:", "http:", "mailto:")):
                continue
            target, _, fragment = unquote(raw).partition("#")
            resolved = (path.parent / target).resolve() if target else path
            assert resolved.exists() or resolved == destination.resolve(), (name, raw)
            if fragment:
                assert resolved.suffix == ".md" and fragment in anchors(resolved), (name, raw)
                fragment_count += 1
            links += 1
    workflow_paths = {}
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        assert "on" in data and data["jobs"]
        scripts = re.findall(r"python(?:3)? (Dia[12]/[^\s]+\.py)", path.read_text(encoding="utf-8"))
        assert scripts and all((ROOT / script).exists() for script in scripts)
        workflow_paths[path.name] = scripts
    for day in ["Dia1", "Dia2"]:
        pattern = "Exercicio-0[1-4]-*.md"
        paths = list((ROOT / day).glob(pattern))
        assert sorted(p.name.split("-")[1] for p in paths) == ["01", "02", "03", "04"]
    parts = list((ROOT / "Dia2/Exercicio-03").glob("Parte-0[1-4]-*.md"))
    assert sorted(p.name.split("-")[1] for p in parts) == ["01", "02", "03", "04"]
    gss = [*list((ROOT / "Dia1/Exercicios-GSS/modulo1").glob("dia1_modulo1_*.py")),
           *list((ROOT / "Dia1/Exercicios-GSS/modulo2").glob("dia1_modulo2_*.py"))]
    assert len(gss) == 12
    for module in [1, 2]:
        assert sorted(p.name.split("_")[2] for p in gss if f"modulo{module}" in p.name) == [f"{n:02d}" for n in range(1, 7)]
    audit = read(Path(__file__).with_name("handover-asset-audit.json"))
    assert audit["status"] == "PASS" and sum(x["pages"] for x in audit["slides"]) == 479
    for item in audit["slides"]:
        assert sha(ROOT / item["file"]) == item["sha256"]
    for item in audit["historical_followups"]:
        assert sha(ROOT / "dia2-local/reports" / item["raw"]) == item["raw_sha256"]
        assert sha(ROOT / "dia2-local/reports" / item["comparison"]) == item["comparison_sha256"]
    preserve = read(Path(__file__).with_name("submission-challenge-integrity.json"))
    for name, digest in preserve["historical_report_hashes"].items():
        assert sha(ROOT / "dia2-local/reports" / name) == digest
    for item in preserve["cases"]:
        assert sha(ROOT / "Dia2/Desafio" / item["file"]) == item["file_sha256"]
    original = read(ROOT / "participant-work/day1/synthesis-preservation.json")
    assert sha(ROOT / "participant-work/day1" / original["path"]) == original["sha256"]
    context = read(Path(__file__).with_name("bootstrap-context-version.json"))
    current = {}
    for name, digest in context["files"].items():
        current[name] = sha(ROOT / name)
        if not name.endswith("context/handoff.md"):
            assert current[name] == digest
    assert "handoff version 1.1.0" in (ROOT / "participant-work/starter/context/handoff.md").read_text()
    generic = read(Path(__file__).with_name("starter-generic-1.0.0.json"))
    assert sha(Path(__file__).with_name(generic["archive"])) == generic["archive_sha256"]
    assert read(Path(__file__).with_name("submission-unit-tests.json"))["tests_run"] == 30
    gss_result = read(ROOT / "participant-work/day1/gss-language-final-evidence/execution.json")
    assert gss_result["suite"]["exit_code"] == 0
    assert "Ran 125 tests" in (ROOT / "participant-work/day1/gss-language-final-evidence/offline-suite.txt").read_text()
    assert read(Path(__file__).with_name("maintenance-validation.json"))["status"] == "PASS"
    assert read(Path(__file__).with_name("maintenance-evaluator-smoke.json"))["status"] == "PASS"
    for name in ["audit-handover-assets.py", "validate-handover.py"]:
        ast.parse(Path(__file__).with_name(name).read_text(encoding="utf-8"))
    diff = subprocess.check_output(["rtk", "proxy", "git", "diff", "--", "TASKS.md"], cwd=ROOT, text=True)
    completed = [line[1:] for line in diff.splitlines() if line.startswith("+- [x]")]
    assert len(completed) == 8, len(completed)
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "local_tasks_completed": 8, "requested_batch_size": 10,
              "relative_links_checked": links, "heading_anchors_checked": fragment_count,
              "workflow_script_paths": workflow_paths, "exercise_numbering": "PASS: four per day, four classifier parts and twelve GSS entries",
              "current_starter_file_hashes": current, "generic_starter_archive_unchanged": True,
              "prior_test_evidence": "125 GSS and 30 classifier tests; evidence checked, not rerun",
              "preserved_challenge_records_and_official_inputs": True,
              "observed_remote_main": "1d8707c65666885861a2a90c7e39145f49c65f7b",
              "remote_check": "Initial restricted connection failed; reviewed read-only retry succeeded",
              "external_dependencies": ["Instructor recipient, acceptance and real feedback session",
                                        "Pages publication or accepted existing-host substitution",
                                        "Future new-origin check only if a submission changes"],
              "limits": ["No teacher delivery, session or approval", "No push or deployment",
                         "No training or official challenge inference", "Attribution review does not establish all third-party rights"]}
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(f"PASS: eight local tasks, {links} links, {fragment_count} anchors, workflow paths and preserved evidence")


if __name__ == "__main__":
    main()
