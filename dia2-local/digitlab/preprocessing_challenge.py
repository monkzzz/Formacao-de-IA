"""Explicitly requested official follow-up for the frozen cleanup preview."""

import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import zipfile

from playwright.sync_api import sync_playwright

from .acceptance import evaluate
from .preprocessing_preview import PREVIEW
from .preprocessing_study import NAME, REPORT, digest
from .qa import open_browser
from .train import ROOT

PREFIX = NAME + "-challenge"
SCOPE = "Explicit user-requested official follow-up after prior exposure; reserved independent test still NOT RUN; never training, tuning or model selection"


def path(suffix):
    return ROOT / "reports" / (PREFIX + suffix)


def create(destination, value):
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def verify(freeze):
    for name, value in freeze["preview_files"].items():
        if digest(PREVIEW / name) != value:
            raise ValueError("Frozen preview changed: " + name)
    for name, value in freeze["preserved_files"].items():
        if digest(ROOT / name) != value:
            raise ValueError("Preserved evidence or app changed: " + name)
    if digest(ROOT / freeze["archive"]) != freeze["archive_sha256"]:
        raise ValueError("Frozen archive changed")


def record():
    if any(path(s).exists() for s in ("-freeze.json", "-raw.json", "-comparison.json")):
        raise FileExistsError("Preserve completed official follow-up")
    study = json.loads(REPORT.read_text())
    preview = json.loads((ROOT / "reports" / (NAME + "-preview-freeze.json")).read_text())
    browser_qa = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    if study["selected_variant"] != "small_components" or browser_qa["status"] != "PASS":
        raise ValueError("Require frozen development selection and passing browser parity")
    if digest(REPORT) != preview["study_report_sha256"] or browser_qa["model_sha256"] != study["model_sha256"]:
        raise ValueError("Study, preview and tested weights differ")
    for name, value in preview["files"].items():
        if digest(PREVIEW / name) != value:
            raise ValueError("Development preview changed")
    preserved = dict(study["preserved_sha256"])
    for relative in ("digitlab/preprocessing_challenge.py", "digitlab/acceptance.py",
                     "digitlab/confidence_suite_browser.py", "reports/" + NAME + ".json",
                     "reports/" + NAME + "-browser.json", "reports/" + NAME + "-preview-freeze.json"):
        preserved[relative] = digest(ROOT / relative)
    directory = ROOT / "artifacts" / PREFIX
    directory.mkdir(parents=True, exist_ok=False)
    archive = directory / "frozen-preview.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as bundle:
        for name in preview["files"]:
            bundle.write(PREVIEW / name, name)
    freeze = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "scope": SCOPE,
              "model_sha256": study["model_sha256"], "preprocessing": browser_qa["preprocessing"],
              "preview_files": preview["files"], "preserved_files": preserved,
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": digest(archive),
              "labels_consulted_before_recording": False}
    verify(freeze)
    create(path("-freeze.json"), freeze)
    paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    input_hashes = {p.name: digest(p) for p in paths}

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(PREVIEW)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("request", lambda r: requests.append({"method": r.method, "url": r.url}))
            url = f"http://127.0.0.1:{server.server_port}/"
            page.goto(url)
            page.wait_for_function("window.preview?.ready === true")
            if page.evaluate("preview.model.manifest.sha256") != study["model_sha256"]:
                raise ValueError("Wrong browser weights")
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("preview.records.length === 10 && !preview.busy", timeout=120000)
            records = page.evaluate("preview.records")
            if [r["file"] for r in records] != [p.name for p in paths]:
                raise ValueError("Wrong input ordering")
            if errors or any(r["method"] != "GET" or not r["url"].startswith((url, "blob:")) for r in requests):
                raise ValueError("Page error or non-static request")
            verify(freeze)
            raw = {"status": "PASS", "recorded_utc": datetime.now(timezone.utc).isoformat(), "scope": SCOPE,
                   "model_sha256": study["model_sha256"], "preprocessing": browser_qa["preprocessing"],
                   "freeze_sha256": digest(path("-freeze.json")), "input_sha256": input_hashes,
                   "predictions": records, "browser_version": browser.version, "requests": requests,
                   "page_errors": errors, "comparison": "NOT RUN; raw saved before reference labels"}
            create(path("-raw.json"), raw)
            page.screenshot(path=str(ROOT / "reports/screenshots" / (PREFIX + ".png")), full_page=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("PASS: ten frozen browser predictions saved; labels not consulted")


def compare():
    if path("-comparison.json").exists() or path("-summary.md").exists():
        raise FileExistsError("Preserve completed comparison")
    freeze = json.loads(path("-freeze.json").read_text())
    verify(freeze)
    raw_path = path("-raw.json")
    raw_hash = digest(raw_path)
    raw = json.loads(raw_path.read_text())
    if raw["status"] != "PASS" or raw["freeze_sha256"] != digest(path("-freeze.json")):
        raise ValueError("Require matching frozen raw predictions")
    for name, value in raw["input_sha256"].items():
        if digest(ROOT.parent / "Dia2/Desafio" / name) != value:
            raise ValueError("Official input changed")
    reference = ROOT / "reports/selectable-models-challenge-followup-v1-comparison.json"
    previous = json.loads(reference.read_text())["models"]["captcha-v3"]
    expected = {r["file"]: r["expected"] for r in previous["cases"]}
    result = evaluate(raw["predictions"], expected)
    result.update(scope=SCOPE, raw_sha256=raw_hash, reference_sha256=digest(reference),
                  freeze_sha256=digest(path("-freeze.json")), model_sha256=raw["model_sha256"],
                  preprocessing=raw["preprocessing"], frozen_runtime_and_active_app_unchanged=True)
    create(path("-comparison.json"), result)
    previous_strict = sum(r["correct"] and r["top_score"] > .9 for r in previous["cases"])
    lines = ["# Official follow-up: fixed weights with small-component cleanup", "", SCOPE + ".", "",
             "| Preparation | Correct / 10 | Correct with score strictly >90% / 10 |", "| --- | ---: | ---: |",
             f"| Preserved current preparation (earlier frozen result) | {previous['correct']} | {previous_strict} |",
             f"| Selected cleanup preparation (new frozen follow-up) | {result['correct']} | {result['correct_above_90']} |", "",
             f"Professor acceptance (10/10 correct, every score strictly >90%): **{result['accepted']}**.", "",
             "| File | Expected | Previous prediction / top score | Cleanup prediction / top score | Correct |", "| --- | ---: | --- | --- | --- |"]
    before = {r["file"]: r for r in previous["cases"]}
    for r in raw["predictions"]:
        old = before[r["file"]]
        score = max(r["scores"])
        lines.append(f"| {r['file']} | {expected[r['file']]} | {old['predicted']} / {old['top_score']:.2%} | {r['predicted']} / {score:.2%} | {r['predicted'] == expected[r['file']]} |")
    lines += ["", f"[Freeze]({PREFIX}-freeze.json) · [Raw predictions]({PREFIX}-raw.json) · [Strict comparison]({PREFIX}-comparison.json).", "",
              "Weights are identical; only the already development-selected preparation differs. The comparison uses saved raw "
              "outputs, not score rescaling or label-derived inference. The independent reserved test is NOT RUN: this was "
              "an explicit request for an early official follow-up, not a claim that final independent gates were passed. "
              "No active application change, training, model selection, publication or push followed. Historical records remain preserved. "
              "Do not use this exposed outcome to choose another transform or parameter.", ""]
    with path("-summary.md").open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    verify(freeze)
    if digest(raw_path) != raw_hash:
        raise ValueError("Raw output changed")
    print(json.dumps({k: result[k] for k in ("correct", "correct_above_90", "accepted")}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("record", "compare"), required=True)
    args = parser.parse_args()
    record() if args.stage == "record" else compare()


if __name__ == "__main__":
    main()
