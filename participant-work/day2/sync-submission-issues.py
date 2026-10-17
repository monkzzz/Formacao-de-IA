"""Append reviewed submission status to the six existing personal Issues.

Dry-run by default. Apply only after the evidence commit is published. Credentials
come from Git's helper in memory; no credential contents or HTTP bodies are logged.
Never contacts the instructor, adds comments, or modifies hosting settings.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
BASE = "https://api.github.com/repos/monkzzz/Formacao-de-IA"
MARKER = "\n<!-- submission-followup-status -->\n"

STATUS = {
    2: ("open", "Evidence index, source reviews and explicit lifecycle coverage are delivered. The participant confirmed continuing the existing approach while preserving dia2-local. That bounded present review is recorded separately from the original design-approval/process gap and instructor assessment; no retrospective approval is invented.",
        ["submission-evidence-index.md", "reference-issue-pr-review.md", "reference-application-review.md", "lifecycle-issue-coverage.md"]),
    3: ("open", "Browser-weight recovery passed in an isolated environment. A fresh dependency install, copied IDX/split/source/baseline checks and 44 local font identities passed. Full retraining was not run; portable public checkpoint/font availability remains unestablished, so this broader artifact Issue remains open.",
        ["submission-artifacts.md", "ml-process-reproduction.md", "ml-reproducibility-preflight.json"]),
    4: ("closed", "Verification acceptance is satisfied by the recorded 30-test suite, actual public browser/parity/interactions and the new selected-model re-evaluation in original and clean environments. Both measured 9910/10000 clean MNIST with identical historical confusion. Two new helper tests passed. Physical touchscreen and optional external readers are not newly tested; no official challenge rerun or production change occurred.",
        ["submission-unit-tests.json", "submission-browser-delivery.md", "ml-process-reproduction.md", "selected-mnist-clean-reevaluation.json"]),
    5: ("open", "Existing-origin browser behavior and scoped asset/weight hashes passed. The participant explicitly reconfirmed that dia2-local remains as previous development. No site migration, production change or Pages configuration is performed. GitHub Pages or instructor acceptance of substitution remains pending.",
        ["submission-browser-delivery.md", "reference-application-review.md", "teacher-feedback-packet.md"]),
    6: ("closed", "Preservation/index criteria are satisfied: original and selected-model freezes, ten raw records/scores, separate comparisons, input identities and public follow-up are linked; historical raw exports were individually hash-verified and committed unchanged. MNIST/synthetic/ten-image results remain distinct; all later challenge checks remain follow-ups. No training/tuning or new official challenge inference occurred.",
        ["submission-challenge-chain.md", "submission-challenge-integrity.json", "teaching-assets-review.md"]),
    7: ("open", "Instructor contact remains explicitly deferred. No instructor acceptance or teacher feedback session is claimed. Current assistant, personal-fork chronology and existing-host differences remain documented; the request/packet are prepared and unsent.",
        ["instructor-process-request.md", "teacher-feedback-packet.md"]),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("Use the full published evidence commit SHA")
    if args.report.exists():
        parser.error("Report exists; preserve prior receipts")
    headers = {"User-Agent": "course-submission-issue-sync", "Accept": "application/vnd.github+json"}
    if args.apply:
        credential = subprocess.run(["rtk", "proxy", "git", "credential", "fill"],
                                    input="protocol=https\nhost=github.com\n\n", text=True,
                                    capture_output=True, timeout=30,
                                    env=os.environ | {"GIT_TERMINAL_PROMPT": "0"})
        values = dict(line.split("=", 1) for line in credential.stdout.splitlines() if "=" in line)
        if credential.returncode or not values.get("password"):
            raise SystemExit("Git credential helper unavailable; no secret values logged")
        headers["Authorization"] = "Bearer " + values["password"]

    def request(url, data=None):
        payload = json.dumps(data).encode() if data is not None else None
        req = Request(url, data=payload, headers=headers, method="PATCH" if payload else "GET")
        if payload:
            req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=60) as response:
            return json.load(response)

    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL",
              "operation": "apply-reviewed-status" if args.apply else "dry-run", "evidence_commit": args.commit, "issues": []}
    try:
        # Refuse to link a nonexistent evidence commit when applying external changes.
        if args.apply:
            assert request(BASE + "/commits/" + args.commit)["sha"] == args.commit
        for number, (state, summary, files) in STATUS.items():
            issue = request(BASE + f"/issues/{number}")
            original = (issue.get("body") or "").split(MARKER)[0]
            links = "\n".join(f"- [{name}](https://github.com/monkzzz/Formacao-de-IA/blob/{args.commit}/participant-work/day2/{name})" for name in files)
            body = original + MARKER + "## Submission follow-up — 2026-10-17\n\n" + summary + "\n\nEvidence:\n" + links + "\n"
            change = {"body": body, "state": state}
            if state == "closed":
                change["state_reason"] = "completed"
            updated = request(BASE + f"/issues/{number}", change) if args.apply else issue
            if args.apply:
                assert updated["body"] == body and updated["state"] == state
            record["issues"].append({"number": number, "url": issue["html_url"], "state_before": issue["state"],
                                     "state_after": updated["state"], "proposed_state": state,
                                     "body_sha256": hashlib.sha256(body.encode()).hexdigest(), "proposed_body": body})
            args.report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        record["status"] = "PASS"
    except HTTPError as error:
        record["error"] = f"GitHub HTTP {error.code}; no HTTP body or credential logged"
        raise SystemExit(record["error"]) from None
    finally:
        args.report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {record['operation']}, {len(record['issues'])} existing Issues; no comments or teacher messages")


if __name__ == "__main__":
    main()
