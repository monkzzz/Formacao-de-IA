"""Inspect/configure the personal Pages site and dispatch its manual workflow."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "https://api.github.com/repos/monkzzz/Formacao-de-IA"


def api_client():
    credential = subprocess.run(
        ["rtk", "proxy", "git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n", text=True, capture_output=True,
        timeout=30, env=os.environ | {"GIT_TERMINAL_PROMPT": "0"},
    )
    values = dict(line.split("=", 1) for line in credential.stdout.splitlines() if "=" in line)
    if credential.returncode or not values.get("password"):
        raise SystemExit("Git credential helper unavailable; no secret logged")
    headers = {"User-Agent": "course-pages", "Accept": "application/vnd.github+json",
               "Authorization": "Bearer " + values["password"]}

    def request(path, method="GET", data=None):
        payload = json.dumps(data).encode() if data is not None else None
        req = Request(BASE + path, data=payload, headers=headers, method=method)
        if payload:
            req.add_header("Content-Type", "application/json")
        try:
            with urlopen(req, timeout=45) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except HTTPError as error:
            if error.code == 404 and method == "GET":
                return None
            raise RuntimeError(f"GitHub HTTP {error.code} for {method} {path}; credentials/body omitted") from None

    return request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["inspect", "enable", "dispatch", "runs"])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("Preserve prior receipts; choose a new report")
    api = api_client()
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "action": args.action}
    if args.action in ("inspect", "enable"):
        before = api("/pages")
        record["before"] = before
        if args.action == "enable":
            if before and before.get("cname"):
                raise SystemExit("Existing custom Pages domain found; review before changing")
            if before is None:
                api("/pages", "POST", {"build_type": "workflow"})
            elif before.get("build_type") != "workflow":
                api("/pages", "PUT", {"build_type": "workflow"})
            record["after"] = api("/pages")
            assert record["after"]["build_type"] == "workflow"
        record["repository_permissions"] = api("").get("permissions")
    elif args.action == "dispatch":
        api("/actions/workflows/digit-lab-pages.yml/dispatches", "POST", {"ref": "main"})
        record["dispatched_ref"] = "main"
    else:
        runs = api("/actions/workflows/digit-lab-pages.yml/runs?per_page=5")
        record["runs"] = [{k: run.get(k) for k in ("id", "html_url", "head_sha", "status", "conclusion", "created_at")}
                          for run in (runs or {}).get("workflow_runs", [])]
        for run in record["runs"]:
            jobs = api(f"/actions/runs/{run['id']}/jobs")
            run["jobs"] = [{k: job.get(k) for k in ("name", "conclusion", "steps")} for job in jobs["jobs"]]
    record["status"] = "PASS"
    args.report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=True))


if __name__ == "__main__":
    main()
