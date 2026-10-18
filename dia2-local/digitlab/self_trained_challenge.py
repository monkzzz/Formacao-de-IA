"""Explicit frozen official rerun in the participant-trained submission package."""

import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .acceptance import evaluate
from .qa import open_browser
from .residual import ResidualCNN
from .self_trained_submission import NAME, digest
from .self_trained_submission_qa import wait
from .train import ROOT

PREFIX = NAME + "-challenge-rerun-v1"
SCOPE = "Explicit user-requested official rerun in the frozen participant-trained package; historical exposure, no training, tuning or selection"


def path(suffix):
    return ROOT / "reports" / (PREFIX + suffix)


def create(p, value):
    with p.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def verify(freeze):
    site = Path(freeze["site"])
    for name,value in freeze["site_sha256"].items():
        if digest(site / name) != value:
            raise ValueError("Submission file changed: " + name)
    for name,value in freeze["evidence_sha256"].items():
        if digest(ROOT / name) != value:
            raise ValueError("Frozen evidence changed: " + name)
    for name,value in freeze["active_assets_sha256"].items():
        if digest(ROOT / name) != value:
            raise ValueError("Active app changed: " + name)
    if digest(Path(freeze["archive"])) != freeze["archive_sha256"]:
        raise ValueError("Submission archive changed")


def record(allow_official):
    if not allow_official:
        raise ValueError("Official rerun requires explicit authorization")
    if path("-freeze.json").exists() or path("-raw.json").exists():
        raise FileExistsError("Preserve completed rerun")
    build_path = ROOT / "reports" / (NAME + "-build.json")
    build = json.loads(build_path.read_text())
    qa_path = ROOT / "reports" / (NAME + "-browser-retry.json")
    qa = json.loads(qa_path.read_text())
    if build["status"] != "PASS" or qa["status"] != "PASS" or qa["build_sha256"] != digest(build_path):
        raise ValueError("Require frozen build and matching passing browser QA")
    site = Path(build["output"])
    manifest = json.loads((site / "model/captcha-v3/digits/manifest.json").read_text())
    evidence = ["digitlab/self_trained_challenge.py", "digitlab/self_trained_submission_qa.py",
                "digitlab/acceptance.py", "digitlab/confidence_suite_browser.py", "digitlab/preprocess.py",
                "digitlab/residual.py", "artifacts/captcha-v3/best.pt",
                str(build_path.relative_to(ROOT)), str(qa_path.relative_to(ROOT))]
    freeze = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "scope": SCOPE,
              "site": str(site), "site_sha256": build["files_sha256"],
              "archive": build["archive"], "archive_sha256": build["archive_sha256"],
              "evidence_sha256": {p: digest(ROOT / p) for p in evidence},
              "active_assets_sha256": build["active_assets_preserved"],
              "model_sha256": manifest["sha256"], "dataset": "captcha-v3",
              "preprocessing": manifest["preprocessing"], "labels_consulted_before_raw_recording": False}
    verify(freeze)
    create(path("-freeze.json"), freeze)
    paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    raw = {"status": "FAIL", "scope": SCOPE, "freeze_sha256": digest(path("-freeze.json")),
           "input_sha256": {p.name: digest(p) for p in paths}, "model_sha256": manifest["sha256"],
           "comparison": "NOT RUN; raw recording precedes reference labels"}

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            url = f"http://127.0.0.1:{server.server_port}/"
            requests, blocked, errors = [], [], []
            def route(request):
                if request.request.url.startswith((url, "blob:", "data:")):
                    request.continue_()
                else:
                    blocked.append(request.request.url)
                    request.abort()
            page.route("**/*", route)
            page.on("request", lambda r: requests.append({"url": r.url, "method": r.method}))
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url)
            wait(page, "Boolean(window.submission?.state.ready)")
            page.locator("#dataset").select_option("captcha-v3")
            wait(page, "submission.state.ready&&!submission.state.busy&&submission.state.dataset==='captcha-v3'")
            if page.evaluate("submission.state.model.manifest.sha256") != manifest["sha256"]:
                raise ValueError("Wrong selected weights")
            page.locator("#files").set_input_files([str(p) for p in paths])
            wait(page, "!submission.state.busy&&submission.state.records.length===10")
            exported = page.evaluate("submission.exportRecord()")
            records = exported["predictions"]
            if [r["file"] for r in records] != [p.name for p in paths]:
                raise ValueError("Wrong input order")
            if any(r.get("error") or r["model_sha256"] != manifest["sha256"] for r in records):
                raise ValueError("Upload error or wrong model identity")
            if blocked or errors or any(r["method"] != "GET" for r in requests):
                raise ValueError("External request, page error or non-static request")
            verify(freeze)
            raw.update(status="PASS", recorded_utc=datetime.now(timezone.utc).isoformat(), raw=exported,
                       browser_version=browser.version, requests=requests, blocked_external_requests=blocked, page_errors=errors)
            page.screenshot(path=str(ROOT / "reports/screenshots" / (PREFIX + ".png")), full_page=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        create(path("-raw.json"), raw)
    print("PASS: all ten raw browser predictions saved before comparison")


def compare():
    if path("-comparison.json").exists() or path("-summary.md").exists():
        raise FileExistsError("Preserve completed comparison")
    freeze = json.loads(path("-freeze.json").read_text())
    verify(freeze)
    raw_hash = digest(path("-raw.json"))
    raw = json.loads(path("-raw.json").read_text())
    if raw["status"] != "PASS" or raw["freeze_sha256"] != digest(path("-freeze.json")):
        raise ValueError("Require passing matched raw recording")
    reference = ROOT / "reports/selectable-models-challenge-followup-v1-comparison.json"
    previous = json.loads(reference.read_text())["models"]["captcha-v3"]
    expected = {r["file"]: r["expected"] for r in previous["cases"]}
    result = evaluate(raw["raw"]["predictions"], expected)
    result.update(scope=SCOPE, raw_sha256=raw_hash, reference_sha256=digest(reference), model_sha256=raw["model_sha256"])
    create(path("-comparison.json"), result)
    torch.set_num_threads(2)
    network = ResidualCNN().eval()
    network.load_state_dict(torch.load(ROOT / "artifacts/captcha-v3/best.pt", map_location="cpu", weights_only=True))
    from .preprocess import prepare
    maximum = 0.
    for row in raw["raw"]["predictions"]:
        source = ROOT.parent / "Dia2/Desafio" / row["file"]
        if digest(source) != raw["input_sha256"][row["file"]]:
            raise ValueError("Official input identity changed")
        x = prepare(np.asarray(Image.open(source).convert("RGBA")), 64)
        np.testing.assert_allclose(x.flatten(), row["input"], atol=1e-6, rtol=0)
        with torch.no_grad():
            scores = network(torch.from_numpy(x[None])).softmax(1).numpy()[0]
        maximum = max(maximum, float(np.max(np.abs(scores - row["scores"]))))
        if maximum > 1e-5 or int(scores.argmax()) != row["predicted"]:
            raise ValueError("Python/browser prediction mismatch")
    verify(freeze)
    if digest(path("-raw.json")) != raw_hash:
        raise ValueError("Raw recording changed")
    create(path("-validation.json"), {"status": "PASS", "cases": 10, "prepared_input_parity": "PASS",
           "maximum_score_error": maximum, "predictions_match_python": True,
           "submission_archive_and_active_app_preserved": True, "raw_sha256": raw_hash,
           "no_external_requests": True, "training_tuning_selection": "NOT RUN"})
    lines = ["# CAPTCHA rerun in the participant-trained submission", "", SCOPE + ".", "",
             f"Preserved residual CNN: **{result['correct']}/10 correct**, **{result['correct_above_90']}/10 correct with original score strictly >90%**. "
             f"Professor criterion met: **{result['accepted']}**.", "",
             "| File | Expected | Predicted | Original top score | Correct and >90% |", "| --- | ---: | ---: | ---: | --- |"]
    for row, accepted in zip(raw["raw"]["predictions"], result["cases"]):
        lines.append(f"| {row['file']} | {expected[row['file']]} | {row['predicted']} | {max(row['scores']):.2%} | {accepted['passes']} |")
    lines += ["", f"[Freeze]({PREFIX}-freeze.json) · [Raw browser output]({PREFIX}-raw.json) · [Strict comparison]({PREFIX}-comparison.json) · [Python/browser and preservation verification]({PREFIX}-validation.json).", "",
              "The residual model was selected explicitly before this rerun. The submission still defaults to the MNIST-only course model; this result belongs to its separately labelled residual extension. "
              "No weights, preprocessing, submission archive, existing website or score display were changed. No training or selection followed this known-image result.", ""]
    with path("-summary.md").open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    print(json.dumps({k: result[k] for k in ("correct", "correct_above_90", "accepted")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("record", "compare"), required=True)
    parser.add_argument("--allow-official-followup", action="store_true")
    args = parser.parse_args()
    record(args.allow_official_followup) if args.stage == "record" else compare()
