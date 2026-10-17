"""Close the hosting Issue with published evidence for the authorized separate Pages site."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists() or not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("Use a published full commit and new receipt path")
    api = runpy.run_path(str(HERE / "github-pages.py"))["api_client"]()
    assert api("/commits/" + args.commit)["sha"] == args.commit
    before = api("/issues/5")
    marker = "\n<!-- pages-publication-completed -->\n"
    body = before["body"].split(marker)[0] + marker + "## Separate Pages publication — 2026-10-17\n\n"
    body += ("The participant explicitly requested the GitHub Pages task after the earlier preservation-only scope. "
             "The app is now published separately at https://monkzzz.github.io/Formacao-de-IA/ . "
             "This supersedes the earlier hosting-substitution dependency. The original site and tracked dia2-local remain intact. "
             "All 55 live assets match the build; real digit/letter parity, 36 uploads, mouse/emulated touch drawing, "
             "real activations and error recovery passed. No physical touchscreen or optional OCR test is claimed. "
             "The selected frozen weight identity and runtime are preserved; an optional official-image rerun was rejected "
             "by automatic approval review and was not executed. No new accuracy claim, training or tuning. "
             "Teacher/process acceptance stays separately open in #7.\n\n")
    for name in ["pages-publication.md", "pages-public-parity.json", "pages-public-interactions-verified.json", "pages-deployment-run.json", "pages-validation.json"]:
        body += f"- [{name}](https://github.com/monkzzz/Formacao-de-IA/blob/{args.commit}/participant-work/day2/{name})\n"
    updated = api("/issues/5", "PATCH", {"body": body, "state": "closed", "state_reason": "completed"})
    assert updated["state"] == "closed" and updated["body"] == body
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "issue": updated["html_url"], "state_before": before["state"], "state_after": updated["state"],
              "evidence_commit": args.commit, "body": body, "scope": "Hosting Issue only; no teacher contact"}
    args.report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("PASS: Issue #5 closed with published Pages evidence")


if __name__ == "__main__":
    main()
