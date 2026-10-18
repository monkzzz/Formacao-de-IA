"""Record a frozen, user-authorized official follow-up for every current digit option."""

import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading

from playwright.sync_api import sync_playwright

from .acceptance import evaluate
from .qa import open_browser
from .self_trained_pages_qa import wait
from .train import ROOT


NAME = "release-3.11.1-all-captcha-followup-v1"
SCOPE = "Explicit user-requested official follow-up after prior exposure; no training, tuning, default changes or model selection"
MODELS = {"mnist": "model", "mnist-supplementary-v1": "model/mnist-supplementary-v1/digits",
          "captcha-v3": "model/captcha-v3/digits"}
CONFIGURATIONS = (
    [{"id": "full-" + name, "site": "full", "cnn": name} for name in MODELS]
    + [{"id": "full-" + reader, "site": "full", "reader": reader, "profile": "standard"}
       for reader in ("ddddocr", "ddddocr-old", "captcha-digits")]
    + [{"id": f"full-{reader}-{profile}", "site": "full", "reader": reader, "profile": profile}
       for reader in ("printed", "handwritten") for profile in ("standard", "precise")]
    + [{"id": "submission-" + name, "site": "submission", "cnn": name} for name in MODELS]
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output(suffix):
    return ROOT / "reports" / (NAME + suffix)


def create(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def verify(freeze):
    for name, checksum in freeze["preserved_sha256"].items():
        if digest(ROOT / name) != checksum:
            raise ValueError("Frozen source/evidence changed: " + name)
    for site, files in freeze["sites"].items():
        for name, checksum in files.items():
            if digest(ROOT / "artifacts" / NAME / site / name) != checksum:
                raise ValueError("Frozen snapshot changed: " + site + "/" + name)


def freeze_runtime():
    destinations = [output(s) for s in ("-freeze.json", "-comparison.json", "-summary.md")]
    destinations += [output("-" + c["id"] + "-raw.json") for c in CONFIGURATIONS]
    destinations += [ROOT / "reports/screenshots" / (NAME + "-" + c["id"] + ".png") for c in CONFIGURATIONS]
    directory = ROOT / "artifacts" / NAME
    if directory.exists() or any(p.exists() for p in destinations):
        raise FileExistsError("Preserve prior follow-up; do not reuse its identity")
    receipt_path = ROOT / "reports/self-trained-submission-cleanup-v4-build.json"
    receipt = json.loads(receipt_path.read_text())
    if receipt["status"] != "PASS" or digest(Path(receipt["archive"])) != receipt["archive_sha256"]:
        raise ValueError("Require intact reviewed submission archive")
    preserved = {receipt_path, Path(__file__), ROOT / "digitlab/acceptance.py",
                 ROOT / "digitlab/confidence_suite_browser.py", ROOT / "digitlab/qa.py"}
    # Preserve historical official evidence without consulting its labels for inference.
    preserved.update(p for p in (ROOT / "reports").glob("*challenge*.json") if not p.name.startswith(NAME))
    sites = {}
    for site, source in (("full", ROOT / "dist"), ("submission", Path(receipt["output"]))):
        files = {p.relative_to(source).as_posix(): digest(p) for p in source.rglob("*")
                 if p.is_file() and p.suffix.lower() not in (".sfc", ".smc")}
        if site == "submission" and files != receipt["files_sha256"]:
            raise ValueError("Submission differs from reviewed package")
        for name, folder in MODELS.items():
            manifest = json.loads((source / folder / "manifest.json").read_text())
            if digest(source / folder / "weights.bin") != manifest["sha256"]:
                raise ValueError("Invalid model weights: " + name)
        for name in files:
            path = source / name
            preserved.add(path)
            target = directory / site / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        sites[site] = files
    for name in ("release-cleanup-3.11.1-public-assets.json", "self-trained-pages-cleanup-v4-public-assets.json"):
        path = ROOT / "reports" / name
        checked = json.loads(path.read_text())
        if checked["status"] != "PASS":
            raise ValueError("Require completed public release identity checks")
        site = "full" if name.startswith("release-") else "submission"
        if any(sites[site].get(row["file"]) != row["sha256"] for row in checked["files"]):
            raise ValueError("Snapshot differs from publicly verified release")
        preserved.add(path)
    freeze = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "scope": SCOPE,
              "configurations": CONFIGURATIONS, "sites": sites,
              "preserved_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sorted(preserved)},
              "official_images_used_before_freeze": False, "labels_consulted_for_inference": False,
              "execution": "Real local browser UI, frozen copies of both publicly verified release artifacts; external pretrained model downloads allowed, image uploads forbidden",
              "coverage": "All current digit options and both TrOCR precision profiles; letter models and Words transcription are outside the single-digit task"}
    verify(freeze)
    create(output("-freeze.json"), freeze)
    print("PASS: frozen 13 configurations before opening official inputs", flush=True)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def record():
    freeze = json.loads(output("-freeze.json").read_text())
    verify(freeze)
    paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    hashes = {p.name: digest(p) for p in paths}
    # A partial run can continue only with configurations never recorded before.
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        for config in CONFIGURATIONS:
            destination = output("-" + config["id"] + "-raw.json")
            if destination.exists():
                previous = json.loads(destination.read_text())
                if previous["status"] != "PASS" or previous["freeze_sha256"] != digest(output("-freeze.json")):
                    raise ValueError("Preserve failed/mismatched attempt; do not retry official search")
                continue
            print("START " + config["id"], flush=True)
            source = ROOT / "artifacts" / NAME / config["site"]
            server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(source)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            url = f"http://127.0.0.1:{server.server_port}/"
            raw = {"status": "FAIL", "scope": SCOPE, "configuration": config,
                   "freeze_sha256": digest(output("-freeze.json")), "input_sha256": hashes,
                   "browser_version": browser.version, "comparison": "NOT RUN; reference labels not consulted during recording"}
            context = browser.new_context(viewport={"width": 1440, "height": 1100})
            requests, blocked, errors = [], [], []

            def guard(route):
                request = route.request
                if request.method != "GET" or request.post_data is not None:
                    blocked.append({"url": request.url, "method": request.method})
                    route.abort()
                else:
                    route.continue_()

            context.route("**/*", guard)
            context.on("request", lambda r: requests.append({"method": r.method, "url": r.url,
                                                            "has_body": r.post_data is not None}))
            page = context.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            try:
                page.goto(url)
                if config["site"] == "full":
                    page.wait_for_function("window.digitLab?.state.ready&&!digitLab.state.loading", timeout=60000)
                    if "cnn" in config:
                        page.locator("#cnn-model").select_option(config["cnn"])
                        page.wait_for_function("key=>digitLab.state.digitExperiment===key&&!digitLab.state.loading", arg=config["cnn"])
                    else:
                        page.locator("#digit-reader").select_option(config["reader"])
                        if config["reader"] in ("printed", "handwritten"):
                            page.locator("#digit-quality").select_option(config["profile"])
                    page.locator("#files").set_input_files([str(p) for p in paths])
                    page.wait_for_function("digitLab.state.uploads.length===10&&!digitLab.state.busy", timeout=600000)
                    exported = page.evaluate("digitLab.exportRecord()")
                else:
                    wait(page, "Boolean(window.submission?.state.ready)")
                    page.locator("#dataset").select_option(config["cnn"])
                    wait(page, "key=>submission.state.ready&&!submission.state.busy&&submission.state.dataset===key", config["cnn"])
                    page.locator("#files").set_input_files([str(p) for p in paths])
                    wait(page, "submission.state.records.length===10&&!submission.state.busy")
                    exported = page.evaluate("submission.exportRecord()")
                raw["export"] = exported
                rows = exported["predictions"]
                if [r["file"] for r in rows] != [p.name for p in paths]:
                    raise ValueError("Unexpected input order")
                if "cnn" in config:
                    manifest = json.loads((source / MODELS[config["cnn"]] / "manifest.json").read_text())
                    if any(r["model_sha256"] != manifest["sha256"] for r in rows):
                        raise ValueError("Wrong selected model")
                else:
                    if any(r["reader"] != config["reader"] or r["profile"] != config["profile"] for r in rows):
                        raise ValueError("Wrong reader/profile")
                if config["site"] == "full" and any(r.get("file_sha256") != hashes[r["file"]] for r in rows):
                    raise ValueError("Input identity mismatch")
                if errors or blocked or any(r.get("error") for r in rows):
                    raise ValueError("Page/network/inference failure; inspect raw evidence")
                verify(freeze)
                page.screenshot(path=str(ROOT / "reports/screenshots" / (NAME + "-" + config["id"] + ".png")), full_page=True)
                raw.update(status="PASS", recorded_utc=datetime.now(timezone.utc).isoformat())
            finally:
                raw.update(requests=requests, blocked_requests=blocked, page_errors=errors)
                create(destination, raw)
                context.close()
                server.shutdown()
                server.server_close()
            print("SAVED " + config["id"] + ": ten raw predictions, no label comparison", flush=True)
        browser.close()


def compare_rows(rows, expected):
    if len(rows) != 10 or len(expected) != 10 or {r["file"] for r in rows} != set(expected):
        raise ValueError("Require exactly ten distinct reference/prediction pairs")
    if any(r.get("error") for r in rows):
        raise ValueError("Inference errors are not classification results")
    scored = all(r.get("scores") is not None for r in rows)
    if not scored and any(r.get("scores") is not None for r in rows):
        raise ValueError("Inconsistent score availability")
    strict = evaluate(rows, expected) if scored else None
    return {"count": 10, "correct": sum(r.get("predicted") == expected[r["file"]] for r in rows),
            "correct_above_90": strict["correct_above_90"] if strict else None,
            "score_target_met": strict["accepted"] if strict else None,
            "score_policy": strict["policy"] if strict else "NOT AVAILABLE; OCR exposes no class scores, none fabricated",
            "cases": [{"file": r["file"], "expected": expected[r["file"]], "predicted": r.get("predicted"),
                       "raw_text": r.get("raw_text"), "correct": r.get("predicted") == expected[r["file"]],
                       "top_score": max(r["scores"]) if scored else None,
                       "correct_class_score": r["scores"][expected[r["file"]]] if scored else None}
                      for r in rows]}


def compare():
    if output("-comparison.json").exists() or output("-summary.md").exists():
        raise FileExistsError("Preserve completed comparison")
    freeze = json.loads(output("-freeze.json").read_text())
    verify(freeze)
    raws = {}
    for config in CONFIGURATIONS:
        path = output("-" + config["id"] + "-raw.json")
        raw = json.loads(path.read_text())
        if raw["status"] != "PASS" or raw["freeze_sha256"] != digest(output("-freeze.json")):
            raise ValueError("Require all completed raw outputs before opening references")
        if any(digest(ROOT.parent / "Dia2/Desafio" / name) != checksum for name, checksum in raw["input_sha256"].items()):
            raise ValueError("Official input changed")
        raws[config["id"]] = (path, raw)
    # References are read only after all 130 raw predictions are saved durably.
    reference = ROOT / "reports/captcha-v3-challenge-comparison.json"
    expected = {r["file"]: r["expected"] for r in json.loads(reference.read_text())["cases"]}
    results = {}
    for config in CONFIGURATIONS:
        path, raw = raws[config["id"]]
        results[config["id"]] = {**compare_rows(raw["export"]["predictions"], expected),
                                 "raw_sha256": digest(path), "pretrained": "reader" in config,
                                 "eligible_for_no_pretrained_submission": "reader" not in config}
    for model in MODELS:
        if results["full-" + model]["cases"] != results["submission-" + model]["cases"]:
            raise ValueError("Full/submission prediction mismatch: " + model)
    create(output("-comparison.json"), {"status": "PASS", "scope": SCOPE, "results": results,
           "reference_sha256": digest(reference), "freeze_sha256": digest(output("-freeze.json")),
           "full_submission_prediction_parity": "PASS", "training_tuning_or_selection": False})
    lines = ["# All current digit options: official CAPTCHA follow-up", "", SCOPE + ".", "",
             "All ten original images were uploaded through the real browser UI for each of 13 frozen configurations. "
             "Both TrOCR quality profiles were tested. Full-site and restricted submission inference used "
             "local frozen copies of the previously hash-verified public release artifacts. External weights/runtime "
             "were actually downloaded; no OCR stubs or image-upload requests were used. All raw outputs "
             "were saved before reference labels were opened. This is a known-case follow-up, not a fresh blind test.", "",
             "| Configuration | Correct / 10 | Correct with original score >90% / 10 | Pretrained |",
             "| --- | ---: | ---: | --- |"]
    for key, value in results.items():
        above = value["correct_above_90"] if value["correct_above_90"] is not None else "N/A"
        lines.append(f"| {key} | {value['correct']} | {above} | {'yes' if value['pretrained'] else 'no'} |")
    lines += ["", "OCR rows without scores cannot establish the strict confidence criterion. "
              "Pretrained readers are excluded from the restricted submission regardless of results. "
              "Scores from the conditional CAPTCHA digit classifier and CNN softmax scores have different meanings; "
              "none is a calibrated correctness probability. Full-site/submission CNN predictions and scores match.", "",
              "| File | Expected | " + " | ".join(results) + " |",
              "| --- | ---: | " + " | ".join("---" for _ in results) + " |"]
    for i, name in enumerate(expected):
        cells = []
        for result in results.values():
            row = next(r for r in result["cases"] if r["file"] == name)
            text = str(row["predicted"]) if row["predicted"] is not None else "no single digit"
            if row["top_score"] is not None:
                text += f" ({row['top_score']:.2%})"
            cells.append(text + (" ✓" if row["correct"] else " ✗"))
        lines.append(f"| {name} | {expected[name]} | " + " | ".join(cells) + " |")
    lines += ["", f"[Frozen identities]({NAME}-freeze.json) · [Full comparison and raw-output hashes]({NAME}-comparison.json).", "",
              "PASS means recording/integrity checks completed; classification results are reported above. "
              "No training, tuning, model/default change or deployment occurred. Prior evidence is preserved.", ""]
    with output("-summary.md").open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    print(json.dumps({k: {n: v[n] for n in ("correct", "correct_above_90", "score_target_met")} for k, v in results.items()}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("freeze", "record", "compare"), required=True)
    args = parser.parse_args()
    {"freeze": freeze_runtime, "record": record, "compare": compare}[args.stage]()


if __name__ == "__main__":
    main()
