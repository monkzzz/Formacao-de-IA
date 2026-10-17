"""Collect raw predictions from a Digit Lab-compatible browser UI, without labels.

Requires playwright==1.55.0 and Chromium. Official inputs require explicit consent.
"""

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def input_files(directory, allow_official):
    directory = directory.resolve()
    official = Path(__file__).resolve().parent
    paths = sorted(directory.glob("*.png"))
    if not paths:
        raise ValueError("No PNG inputs found")
    if not allow_official and any(path.resolve().parent == official for path in paths):
        raise ValueError("Official inputs require --allow-official-followup")
    return paths


def validate_predictions(records, paths, model_hash):
    if len(records) != len(paths):
        raise ValueError("Prediction count differs from uploaded image count")
    for record, path in zip(records, paths):
        if record.get("error"):
            raise ValueError(f"Upload failed for {path.name}: {record['error']}")
        if record.get("file") != path.name or record.get("model_sha256") != model_hash:
            raise ValueError("Prediction filename/model identity mismatch")
        if record.get("file_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError("Uploaded image hash mismatch")
        scores = record.get("scores", [])
        if len(scores) != 10 or any(not isinstance(x, (int, float)) or not math.isfinite(x)
                                   or x < 0 or x > 1 for x in scores):
            raise ValueError("Expected ten finite digit scores between zero and one")
        if abs(sum(scores) - 1) > 1e-5:
            raise ValueError("Digit scores are not normalized")
        if str(record.get("predicted")) != str(max(range(10), key=scores.__getitem__)):
            raise ValueError("Predicted digit differs from score argmax")


def collect(args, report):
    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("--url must be an HTTP(S) application URL")
    paths = input_files(args.input_dir, args.allow_official_followup)
    report["input_hashes"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        options = {"headless": True}
        if args.browser_executable:
            options["executable_path"] = str(args.browser_executable)
        browser = playwright.chromium.launch(**options)
        try:
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(args.url, timeout=60000)
            if response is None or response.status != 200:
                raise ValueError("Application did not return HTTP 200")
            page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
            identity = page.evaluate("digitLab.state.model.manifest.sha256")
            if page.locator("#digit-reader").count() and page.locator("#digit-reader").input_value() != "local":
                raise ValueError("Expected participant-trained default CNN")
            if page.evaluate("digitLab.state.mode") != "digits":
                raise ValueError("Expected digit mode")
            report["model_sha256"] = identity
            report["application_version"] = page.locator("#app-version").inner_text()
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy",
                                   arg=len(paths), timeout=120000)
            report["raw"] = page.evaluate("digitLab.exportRecord()")
            report["page_errors"] = errors
            validate_predictions(report["raw"]["predictions"], paths, identity)
            if errors:
                raise ValueError("Browser page errors occurred")
        finally:
            browser.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Digit Lab-compatible application URL")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-official-followup", action="store_true")
    parser.add_argument("--browser-executable", type=Path, help="Optional installed browser for local checks")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("Output exists; use a new path to preserve earlier evidence")
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "url": args.url,
              "status": "FAIL", "scope": "Deployment follow-up after prior challenge exposure; not training or a blind test",
              "labels_consulted": False, "accuracy": "NOT COMPUTED; compare labels separately"}
    code = 1
    try:
        collect(args, report)
        report["status"] = "PASS"
        code = 0
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(f"{report['status']}: {args.output}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
