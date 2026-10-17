"""Verify a published personal source commit and required Git tree entries."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://api.github.com/repos/monkzzz/Formacao-de-IA"
REQUIRED = ["TASKS.md", "SUBMISSION.md", "participant-work/starter/AGENTS.md",
            "participant-work/starter/.github/skills/bootstrap-project/SKILL.md",
            "participant-work/starter/context/project.md", "participant-work/starter/context/handoff.md",
            "participant-work/day2/starter-generic-1.0.0.zip",
            "participant-work/day2/submission-evidence-index.md",
            "participant-work/day2/independent-task-completion.md",
            "participant-work/day2/ml-process-reproduction.md",
            "participant-work/day2/selected-mnist-clean-reevaluation.json",
            "dia2-local/digitlab/residual.py", "dia2-local/dist/index.html",
            "dia2-local/dist/model/captcha-v3/digits/manifest.json"]


def git(*args):
    return subprocess.check_output(["rtk", "proxy", "git", *args], cwd=ROOT, text=True).strip()


def get(path):
    req = Request(BASE + path, headers={"User-Agent": "course-source-publication-check",
                                       "Accept": "application/vnd.github+json"})
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("Preserve prior receipts; choose a new report")
    commit = git("rev-parse", args.commit)
    remote = git("ls-remote", "origin", "refs/heads/main").split()[0]
    if remote != commit:
        raise SystemExit("Remote main differs from requested published commit; inspect before proceeding")
    returned = get("/commits/" + commit)
    assert returned["sha"] == commit
    tree = get("/git/trees/" + returned["commit"]["tree"]["sha"] + "?recursive=1")
    assert not tree["truncated"]
    entries = {item["path"]: item for item in tree["tree"]}
    for path in REQUIRED:
        assert entries[path]["type"] == "blob"
        assert entries[path]["sha"] == git("rev-parse", commit + ":" + path)
    assert "dia2-local/dist/model/captcha-v3/digits/weights.bin" not in entries
    assert "dia2-local/artifacts/captcha-v3/best.pt" not in entries
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "repository": "https://github.com/monkzzz/Formacao-de-IA", "remote_main": remote,
              "commit_url": returned["html_url"], "tree_sha": returned["commit"]["tree"]["sha"],
              "required_path_blob_sha": {path: entries[path]["sha"] for path in REQUIRED},
              "ignored_model_binaries_not_published_in_git": True,
              "scope": "Source repository publication only; no site, Pages or FTP deployment"}
    with args.report.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print(f"PASS: remote main {remote}, {len(REQUIRED)} required source/evidence entries verified")


if __name__ == "__main__":
    main()
