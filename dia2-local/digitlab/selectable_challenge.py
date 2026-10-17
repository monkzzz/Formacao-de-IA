"""Freeze selectable CNNs, record official browser outputs, then compare separately."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from urllib.parse import urlparse
import zipfile

from playwright.sync_api import sync_playwright

from .confidence_suite_browser import compare_predictions
from .qa import open_browser
from .train import ROOT

NAME = "selectable-models-challenge-followup-v1"
MODELS = {"mnist": "model", "mnist-supplementary-v1": "model/mnist-supplementary-v1/digits",
          "captcha-v3": "model/captcha-v3/digits"}
SCOPE = "User-requested frozen official follow-up after prior exposure; descriptive comparison only, never training, tuning or model selection"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def location(suffix):
    return ROOT / "reports" / (NAME + suffix)


def verify(freeze):
    for name, checksum in freeze["files"].items():
        if digest(ROOT / name) != checksum:
            raise ValueError("Frozen file changed: " + name)
    if digest(ROOT / freeze["archive"]) != freeze["archive_sha256"]:
        raise ValueError("Frozen archive changed")


def record(url):
    if any(location(s).exists() for s in ("-freeze.json", "-raw.json", "-comparison.json")):
        raise FileExistsError("Preserve completed follow-up; no repeated challenge search")
    qa = ROOT / "reports/selectable-models-browser-qa.json"
    audit = ROOT / "reports/selectable-models-validation.json"
    if any(json.loads(p.read_text())["status"] != "PASS" for p in (qa, audit)):
        raise ValueError("Require passing selectable-model browser and integrity checks")
    manifests = {key: json.loads((ROOT / "dist" / path / "manifest.json").read_text()) for key, path in MODELS.items()}
    sources = sorted({p for suffix in ("*.js", "*.css", "*.html") for p in (ROOT / "dist").rglob(suffix)})
    sources += [ROOT / "digitlab/selectable_challenge.py", qa, audit,
                ROOT / "artifacts/mnist-supplementary-v1/selection.json"]
    for key, relative in MODELS.items():
        folder = ROOT / "dist" / relative
        if digest(folder / "weights.bin") != manifests[key]["sha256"]:
            raise ValueError("Model integrity failure: " + key)
        sources += [folder / "weights.bin", folder / "manifest.json"]
    # Preserve completed official and training evidence; never use it during inference.
    sources += [ROOT / "reports" / n for n in ("challenge-raw.json", "challenge-freeze.json",
                "captcha-v3-challenge-raw.json", "captcha-v3-challenge-comparison.json",
                "mnist-supplementary-v1.json", "selectable-models-summary.md")]
    files = {str(p.relative_to(ROOT)): digest(p) for p in sources}
    directory = ROOT / "artifacts" / NAME
    directory.mkdir(parents=True, exist_ok=False)
    archive = directory / "frozen-runtime.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as bundle:
        for p in sources:
            bundle.write(p, str(p.relative_to(ROOT)))
    freeze = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "url": url, "scope": SCOPE,
              "models": {k: {"sha256": m["sha256"], "preprocessing": m["preprocessing"],
                            "architecture": m["architecture"]} for k, m in manifests.items()},
              "files": files, "archive": str(archive.relative_to(ROOT)), "archive_sha256": digest(archive),
              "labels_consulted_for_recording": False, "training_or_tuning_from_results": False}
    create(location("-freeze.json"), freeze)
    # Official inputs are enumerated only after every model and runtime is frozen.
    paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    input_hashes = {p.name: digest(p) for p in paths}
    result = {"status": "FAIL", "scope": SCOPE, "freeze_sha256": digest(location("-freeze.json")),
              "input_sha256": input_hashes, "models": {}, "comparison": "NOT RUN; labels not consulted during collection"}
    requests, errors = [], []
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        result["browser_version"] = browser.version
        for key in MODELS:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append({"method": request.method, "url": request.url}))
            page.goto(url)
            page.wait_for_function("window.digitLab?.state.ready && !digitLab.state.loading", timeout=60000)
            page.locator("#cnn-model").select_option(key)
            page.wait_for_function("key => digitLab.state.digitExperiment === key && !digitLab.state.loading", arg=key)
            if page.evaluate("digitLab.state.model.manifest.sha256") != manifests[key]["sha256"]:
                raise ValueError("Browser model does not match freeze")
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("digitLab.state.uploads.length === 10 && !digitLab.state.busy", timeout=120000)
            raw = page.evaluate("digitLab.exportRecord()")
            if [r["file"] for r in raw["predictions"]] != [p.name for p in paths]:
                raise ValueError("Unexpected official input order")
            if any("error" in r or r["cnn_model"] != key or r["model_sha256"] != manifests[key]["sha256"]
                   or r["file_sha256"] != input_hashes[r["file"]] for r in raw["predictions"]):
                raise ValueError("Upload failed or input/model identity changed")
            result["models"][key] = raw
            page.screenshot(path=str(ROOT / "reports/screenshots" / (NAME + "-" + key + ".png")), full_page=True)
            page.close()
        browser.close()
    origin = urlparse(url).netloc
    if errors or any(r["method"] != "GET" or (urlparse(r["url"]).netloc != origin
                    and not r["url"].startswith(("blob:", "data:"))) for r in requests):
        raise ValueError("Page errors or unexpected non-static request")
    verify(freeze)
    result.update(status="PASS", recorded_utc=datetime.now(timezone.utc).isoformat(), requests=requests, page_errors=errors)
    create(location("-raw.json"), result)
    print("PASS: three frozen models, thirty raw predictions saved; no label comparison")


def compare():
    if location("-comparison.json").exists() or location("-summary.md").exists():
        raise FileExistsError("Preserve completed challenge comparison")
    freeze = json.loads(location("-freeze.json").read_text())
    raw_path = location("-raw.json")
    raw_hash = digest(raw_path)
    raw = json.loads(raw_path.read_text())
    if raw["status"] != "PASS" or raw["freeze_sha256"] != digest(location("-freeze.json")) or set(raw["models"]) != set(MODELS):
        raise ValueError("Require all frozen raw predictions before label comparison")
    verify(freeze)
    for name, checksum in raw["input_sha256"].items():
        if digest(ROOT.parent / "Dia2/Desafio" / name) != checksum:
            raise ValueError("Official input changed")
    # Only after all raw outputs are durable do we open reference labels.
    reference = ROOT / "reports/captcha-v3-challenge-comparison.json"
    expected = {r["file"]: r["expected"] for r in json.loads(reference.read_text())["cases"]}
    if len(expected) != 10:
        raise ValueError("Expected ten preserved reference cases")
    comparisons = {key: compare_predictions(value["predictions"], expected) for key, value in raw["models"].items()}
    result = {"status": "PASS", "scope": SCOPE, "raw_sha256": raw_hash,
              "freeze_sha256": digest(location("-freeze.json")), "reference_sha256": digest(reference),
              "models": {key: {"model_sha256": freeze["models"][key]["sha256"], **value} for key, value in comparisons.items()},
              "training_tuning_or_selection_from_results": False, "public_deployment": "NOT RUN"}
    create(location("-comparison.json"), result)
    lines = ["# Official CAPTCHA follow-up: selectable CNNs", "", SCOPE + ".", "",
             "Models/runtime were frozen together before uploading the ten official inputs. Raw predictions were saved "
             "before reference labels were opened for comparison. No weights, preprocessing, default selection or displayed scores were changed.", "",
             "| Model | Correct / 10 | Correct with score ≥90% / 10 | All-ten confidence target |",
             "| --- | ---: | ---: | --- |"]
    for key, value in comparisons.items():
        lines.append(f"| {key} | {value['correct']} | {value['correct_at_90']} | {value['target_met']} |")
    lines += ["", "Each cell below shows predicted digit, top score, and whether the digit was correct. A confident error remains an error.", "",
              "| File | Expected | MNIST only | Supplementary | Preserved residual |", "| --- | ---: | --- | --- | --- |"]
    for i in range(10):
        rows = [comparisons[k]["cases"][i] for k in MODELS]
        cells = [f"{r['predicted']} · {r['top_score']:.2%} · {'correct' if r['correct'] else 'wrong'}" for r in rows]
        lines.append(f"| {rows[0]['file']} | {rows[0]['expected']} | " + " | ".join(cells) + " |")
    lines += ["", f"[Frozen identities]({NAME}-freeze.json) · [Raw browser outputs]({NAME}-raw.json) · "
              f"[Separate comparison]({NAME}-comparison.json).", "",
              "PASS describes successful recording/integrity checks, not a perfect classification result. "
              "Prior official outcomes were already known, so this is not a fresh blind test or a general CAPTCHA accuracy estimate. "
              "Scores are uncalibrated softmax outputs. The optional extension remains distinct from the required MNIST-only exercise. "
              "Historical reports, model weights and public deployment remain unchanged. Do not use this follow-up to tune another checkpoint.", ""]
    with location("-summary.md").open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    if digest(raw_path) != raw_hash:
        raise ValueError("Raw predictions changed")
    print(json.dumps({k: {"correct": v["correct"], "correct_at_90": v["correct_at_90"]} for k,v in comparisons.items()}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("record", "compare"), required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8882/")
    args = parser.parse_args()
    record(args.url) if args.stage == "record" else compare()


if __name__ == "__main__":
    main()
