"""Check this completion batch without rewriting historical evidence."""

import ast
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent


def read(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    destination = BASE / "independent-validation.json"
    if destination.exists():
        raise SystemExit("Evidence already exists; choose a new destination")
    changed = subprocess.check_output(
        ["rtk", "proxy", "git", "diff", "01804ae", "--name-only"], cwd=ROOT, text=True
    ).splitlines()
    documents = [ROOT / name for name in changed if name.endswith(".md")]
    links = fragments = 0
    for path in documents:
        for raw in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if raw.startswith(("https:", "http:", "mailto:")):
                continue
            target, _, fragment = unquote(raw).partition("#")
            resolved = (path.parent / target).resolve() if target else path
            assert resolved.exists(), (str(path), raw)
            if fragment:
                assert resolved.suffix == ".md" and fragment in anchors(resolved), (str(path), raw)
                fragments += 1
            links += 1
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    for number in range(2, 13):
        assert re.search(rf"^- \[x\] \*\*R{number:02d}\b", tasks, re.MULTILINE)
    assert re.search(r"^- \[ \] \*\*R01\b", tasks, re.MULTILINE)
    assert not subprocess.check_output(
        ["rtk", "proxy", "git", "diff", "01804ae", "--", "dia2-local"], cwd=ROOT
    ), "Protected application changed"
    results = [read(name) for name in ["selected-mnist-reevaluation.json", "selected-mnist-clean-reevaluation.json"]]
    assert results[0]["metrics"] == results[1]["metrics"]
    for result in results:
        assert result["status"] == "PASS" and result["metrics"]["correct"] == 9910
        assert len(result["predictions"]) == 10000
        assert result["preserved_sha256_before"] == result["preserved_sha256_after"]
        for name, digest in result["preserved_sha256_before"].items():
            assert sha(ROOT / name) == digest
    preflight = read("ml-reproducibility-preflight.json")
    assert preflight["status"] == "PASS" and preflight["system_site_packages_disabled"]
    assert len(preflight["font_hashes"]) == 44
    publication = read("source-publication-verification.json")
    issues = read("issue-sync-result.json")
    assert publication["status"] == issues["status"] == "PASS"
    assert publication["remote_main"] == issues["evidence_commit"]
    states = {str(item["number"]): item["state_after"] for item in issues["issues"]}
    assert states == {"2": "open", "3": "open", "4": "closed", "5": "open", "6": "closed", "7": "open"}
    preserved = read("submission-challenge-integrity.json")
    for name, digest in preserved["historical_report_hashes"].items():
        assert sha(ROOT / "dia2-local/reports" / name) == digest
    for item in preserved["cases"]:
        assert sha(ROOT / "Dia2/Desafio" / item["file"]) == item["file_sha256"]
    original = json.loads((ROOT / "participant-work/day1/synthesis-preservation.json").read_text(encoding="utf-8"))
    assert sha(ROOT / "participant-work/day1" / original["path"]) == original["sha256"]
    archive = read("starter-generic-1.0.0.json")
    assert sha(BASE / archive["archive"]) == archive["archive_sha256"]
    parsed = []
    for name in changed + [str(Path(__file__).relative_to(ROOT))]:
        if name.endswith(".py"):
            ast.parse((ROOT / name).read_text(encoding="utf-8"))
            parsed.append(name)
    report = {
        "executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
        "completed_followups": [f"R{n:02d}" for n in range(2, 13)],
        "pending_participant_activity": "R01: actual research critique and direction",
        "documents_checked": [str(path.relative_to(ROOT)) for path in documents],
        "relative_links_checked": links, "heading_anchors_checked": fragments,
        "python_syntax_checked": sorted(set(parsed)),
        "selected_model_correct": [result["metrics"]["correct"] for result in results],
        "selected_model_count_each": 10000,
        "same_metrics_original_and_clean_environments": True,
        "frozen_records_official_inputs_and_application_unchanged": True,
        "source_evidence_commit": publication["remote_main"], "issue_states": states,
        "current_starter_file_hashes": {
            str(path.relative_to(ROOT)): sha(path)
            for path in (ROOT / "participant-work/starter/context").glob("*.md")
        },
        "validation_scope": "Documentation, syntax, evidence and integrity checks; no training, official challenge inference or deployment",
        "behavior_tests": "Two focused helper tests passed earlier in this batch; broader historical suites not rerun",
        "remaining_dependencies": ["Participant research critique", "Instructor decisions and actual feedback", "Hosting requirement or accepted substitution", "Portable checkpoint/font availability remains unestablished"]
    }
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(f"PASS: 11 follow-ups, {links} links, {fragments} anchors, evidence and frozen artifacts")


if __name__ == "__main__":
    main()
