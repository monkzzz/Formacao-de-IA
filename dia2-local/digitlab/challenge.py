"""Freeze the local application and record the first challenge upload run.

This module never reads labels or the challenge generator. Existing first-run
records are immutable: execution refuses to replace them.
"""

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT, write_json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--resume-collection", action="store_true",
                        help="Reuse an unchanged freeze after a collection-harness interruption; never replace raw predictions")
    args = parser.parse_args()
    reports = ROOT / "reports"
    raw_path = reports / "challenge-raw.json"
    freeze_path = reports / "challenge-freeze.json"
    if raw_path.exists() or (freeze_path.exists() and not args.resume_collection):
        raise SystemExit("First-run freeze or predictions already exist. Preserve them; do not overwrite independent evaluation evidence.")
    if args.resume_collection and not freeze_path.exists():
        raise SystemExit("No existing freeze to resume")
    manifest = json.loads((ROOT / "dist/model/manifest.json").read_text(encoding="utf-8"))
    qa = json.loads((reports / "browser-qa.json").read_text(encoding="utf-8"))
    if qa["model_sha256"] != manifest["sha256"] or any(c["status"] != "PASS" for c in qa["checks"].values()):
        raise SystemExit("Passing browser QA for the selected weights is required before challenge evaluation.")
    assert digest(ROOT / "dist/model/weights.bin") == manifest["sha256"]
    source_files = sorted([*ROOT.glob("digitlab/*.py"), *ROOT.glob("dist/*.js"),
                           *ROOT.glob("dist/*.html"), *ROOT.glob("dist/*.css"),
                           ROOT / "dist/model/manifest.json", ROOT / "requirements-lock.txt"])
    sources = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in source_files}
    source_id = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    archive = ROOT / "artifacts/frozen-app.zip"
    if args.resume_collection:
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        # A collector repair must not change the actual model or inference code.
        for name, value in freeze["sources"].items():
            if name != "digitlab/challenge.py" and digest(ROOT / name) != value:
                raise SystemExit(f"Frozen source changed: {name}")
        assert digest(archive) == freeze["archive_sha256"]
        assert manifest["sha256"] == freeze["model_sha256"]
        sources, source_id = freeze["sources"], freeze["source_tree_sha256"]
    else:
        with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted((ROOT / "dist").rglob("*")):
                if path.is_file() and path.name != "parity.json":
                    bundle.write(path, path.relative_to(ROOT / "dist"))
        freeze = {"frozen_at": datetime.now(timezone.utc).isoformat(), "url": args.url,
              "scope": "local browser evaluation; no public deployment claimed",
              "source_tree_sha256": source_id, "sources": sources,
              "model_sha256": manifest["sha256"], "preprocessing": manifest["preprocessing"],
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": digest(archive),
                  "labels_consulted_before_predictions": False}
        with freeze_path.open("x", encoding="utf-8") as handle:
            json.dump(freeze, handle, indent=2)
    # Only enumerate challenge PNGs after the model/application are frozen.
    directory = ROOT.parent / "Dia2/Desafio"
    paths = [directory / f"caso_{i:02d}.png" for i in range(1, 11)]
    if not all(path.is_file() for path in paths):
        raise SystemExit("The ten official challenge PNGs were not found.")
    with sync_playwright() as p:
        browser = open_browser(p)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        requests = []
        page.on("request", lambda request: requests.append({"url": request.url, "method": request.method}))
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready === true", timeout=60000)
        assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
        page.locator("#files").set_input_files([str(path) for path in paths])
        page.wait_for_function("digitLab.state.uploads.length === 10 && !digitLab.state.busy", timeout=60000)
        raw = page.evaluate("digitLab.exportRecord()")
        assert len(raw["predictions"]) == 10
        assert all("predicted" in record and "error" not in record for record in raw["predictions"])
        assert [r["file"] for r in raw["predictions"]] == [p.name for p in paths]
        assert all(request["method"] == "GET" and
                   (request["url"].startswith(args.url) or request["url"].startswith("blob:"))
                   for request in requests), requests
        raw.update({"source_tree_sha256": source_id, "freeze_sha256": digest(freeze_path),
                    "browser_version": browser.version, "requests": requests,
                    "comparison_status": "NOT COMPARED: predictions preserved before answer-key inspection",
                    "collector_sha256": digest(ROOT / "digitlab/challenge.py"),
                    "resumed_collection": args.resume_collection,
                    "collection_note": ("Initial collection stopped before raw output was saved because the network check rejected local blob preview URLs. Only the collection harness was repaired; original frozen model, preprocessing, application, and archive are unchanged. No labels consulted."
                                        if args.resume_collection else "Initial collection")})
        # This is the durable first-run boundary. Labels may be inspected only afterward.
        with raw_path.open("x", encoding="utf-8") as handle:
            json.dump(raw, handle, indent=2, allow_nan=False)
        screenshots = reports / "screenshots"
        screenshots.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshots / "challenge-all.png"), full_page=True)
        for index in range(10):
            page.locator(".upload-result").nth(index).click()
            page.screenshot(path=str(screenshots / f"challenge-{index + 1:02d}.png"), full_page=True)
        browser.close()
    assert all(digest(ROOT / name) == value for name, value in sources.items()
               if not args.resume_collection or name != "digitlab/challenge.py")
    print(json.dumps({"raw_sha256": digest(raw_path), "source_tree_sha256": source_id,
                      "predictions": [{"file": r["file"], "predicted": r["predicted"]} for r in raw["predictions"]]}), flush=True)


if __name__ == "__main__":
    main()
