"""Validate Pages delivery records and documentation without challenge inference."""

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent


def main():
    destination = BASE / "pages-validation.json"
    if destination.exists():
        raise SystemExit("Preserve existing validation")
    anchors = runpy.run_path(str(BASE / "validate-independent-completion.py"))["anchors"]
    documents = ["TASKS.md", "SUBMISSION.md", "participant-work/day2/pages-publication.md",
                 "participant-work/starter/context/project.md", "participant-work/starter/context/decisions.md",
                 "participant-work/starter/context/handoff.md"]
    links = fragments = 0
    for name in documents:
        path = ROOT / name
        for raw in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if raw.startswith(("https:", "http:", "mailto:")):
                continue
            target, _, fragment = unquote(raw).partition("#")
            resolved = (path.parent / target).resolve() if target else path
            assert resolved.exists(), (name, raw)
            if fragment:
                assert fragment in anchors(resolved), (name, raw)
                fragments += 1
            links += 1
    def read(name):
        return json.loads((BASE / name).read_text(encoding="utf-8"))
    public = read("pages-public-interactions-verified.json")
    assert public["status"] == read("pages-public-parity.json")["status"] == "PASS"
    assert read("pages-local-parity.json")["status"] == "PASS"
    run = read("pages-deployment-run.json")["runs"][0]
    assert run["conclusion"] == "success" and run["head_sha"] == public["source_commit"]
    assert len(public["asset_sha256"]) == 55
    manifest = json.loads((ROOT / "dia2-local/dist/model/captcha-v3/digits/manifest.json").read_text())
    freeze = json.loads((ROOT / "dia2-local/reports/captcha-v3-challenge-freeze.json").read_text())
    assert public["model_sha256"] == manifest["sha256"] == freeze["model_sha256"]
    for name in ["build-pages.py", "github-pages.py", "verify-pages.py", "validate-pages.py"]:
        ast.parse((BASE / name).read_text(encoding="utf-8"))
    assert not subprocess.check_output(["rtk", "proxy", "git", "diff", "5e3f2c9", "--", "dia2-local"], cwd=ROOT)
    preserved = read("submission-challenge-integrity.json")
    for name, digest in preserved["historical_report_hashes"].items():
        assert hashlib.sha256((ROOT / "dia2-local/reports" / name).read_bytes()).hexdigest() == digest
    result = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "pages_url": public["url"], "deployment_source_commit": public["source_commit"],
              "deployment_run": run["html_url"], "relative_links_checked": links,
              "anchors_checked": fragments, "live_asset_hashes_checked": 55,
              "local_and_public_real_model_parity": "PASS", "frozen_model_identity": manifest["sha256"],
              "tracked_application_and_historical_reports_unchanged": True,
              "official_image_rerun": "NOT RUN: automatic approval rejection; no workaround",
              "validation_scope": "Live deployment identity, non-challenge browser parity/uploads, drawing and emulated touch; no training or new accuracy measurement"}
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: Pages delivery, {links} links, {fragments} anchors, frozen identities")


if __name__ == "__main__":
    main()
