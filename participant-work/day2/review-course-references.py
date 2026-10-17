"""Capture public reference Issue/PR evidence without modifying GitHub."""

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "https://api.github.com/repos/vcanonici/Formacao-de-IA"


def get(url):
    request = Request(url, headers={"User-Agent": "course-reference-review",
                                   "Accept": "application/vnd.github+json"})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def pages(url):
    items = []
    for page in range(1, 11):
        batch = get(url + ("&" if "?" in url else "?") + f"per_page=100&page={page}")
        items.extend(batch)
        if len(batch) < 100:
            return items
    raise RuntimeError("Pagination exceeds bounded review; preserve partial data and investigate")


def main():
    destination = HERE / "reference-github-review.json"
    if destination.exists():
        raise SystemExit("Evidence exists; use a new destination")
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL",
              "scope": "Public read-only reference review; no execution, comments or mutations"}
    try:
        issue = get(BASE + "/issues/1")
        record["issue"] = {key: issue.get(key) for key in ["number", "title", "html_url", "state", "body", "created_at", "updated_at"]}
        record["issue_comments"] = pages(BASE + "/issues/1/comments")
        pr = get(BASE + "/pulls/2")
        record["pull_request"] = {key: pr.get(key) for key in ["number", "title", "html_url", "state", "merged", "mergeable_state", "body", "created_at", "updated_at", "additions", "deletions", "changed_files"]}
        record["pull_request"].update(head_sha=pr["head"]["sha"], base_sha=pr["base"]["sha"])
        record["pr_conversation"] = pages(BASE + "/issues/2/comments")
        record["pr_reviews"] = pages(BASE + "/pulls/2/reviews")
        record["pr_review_comments"] = pages(BASE + "/pulls/2/comments")
        record["pr_files"] = pages(BASE + "/pulls/2/files")
        sha = pr["head"]["sha"]
        record["pr_check_runs"] = get(BASE + f"/commits/{sha}/check-runs?per_page=100")
        record["pr_commit_status"] = get(BASE + f"/commits/{sha}/status")
        record["reference_application_commit"] = get("https://api.github.com/repos/vcanonici/Image-classifier-demo/commits/main")["sha"]
        record["personal_issues_before"] = pages("https://api.github.com/repos/monkzzz/Formacao-de-IA/issues?state=all")
        record["status"] = "PASS"
    except Exception as error:
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        destination.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "issue": record["issue"]["title"],
                      "pr": record["pull_request"]["title"], "files": len(record["pr_files"]),
                      "checks": record["pr_check_runs"]["total_count"],
                      "reference_application_commit": record["reference_application_commit"]}))


if __name__ == "__main__":
    main()
