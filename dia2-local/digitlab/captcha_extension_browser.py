"""Isolated actual-app export, browser QA and conditional official follow-up."""

import argparse
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import shutil
import threading

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .acceptance import evaluate
from .captcha_extension import DIRECTORY, NAME, POLICY, REPORT, baseline_model, digest, read_cache, selected
from .highres import export as export_weights
from .preprocess import prepare
from .qa import open_browser
from .residual import ARCHITECTURE
from .train import ROOT, write_json

PREVIEW = ROOT / ".tmp" / (NAME + "-preview")
FREEZE = DIRECTORY / "runtime-freeze.json"


def verify_preview(freeze):
    if digest(ROOT / "digitlab/captcha_extension_browser.py") != freeze["helper_sha256"]:
        raise ValueError("Frozen browser helper changed")
    for name, value in freeze["files"].items():
        if digest(PREVIEW / name) != value:
            raise ValueError("Frozen preview changed: " + name)


def export():
    metadata, selection = selected()
    if PREVIEW.exists() or FREEZE.exists():
        raise FileExistsError("Preserve existing isolated candidate")
    model = baseline_model()
    model.load_state_dict(torch.load(DIRECTORY / "best.pt", map_location="cpu", weights_only=True))
    raw_x, _ = read_cache("raw")
    shutil.copytree(ROOT / "dist", PREVIEW, ignore=shutil.ignore_patterns("roms", "*.sfc"))
    folder = PREVIEW / "model/captcha-v3/digits"
    for name in ("weights.bin", "manifest.json", "parity.json"):
        (folder / name).unlink(missing_ok=True)
    folder.rmdir()
    training = metadata | {"test": metadata["validation"]["mnist"],
                           "split": {"train": 48600, "validation": POLICY["development_count"]}}
    manifest = export_weights(model, folder, training, raw_x[:10])
    manifest.update(architecture=ARCHITECTURE, evaluation_label="MNIST validation · candidate preview")
    write_json(folder / "manifest.json", manifest)
    app_path = PREVIEW / "v3/app.js"
    source = app_path.read_text()
    old = 'digitExperiment: "mnist"'
    if source.count(old) != 1:
        raise ValueError("Unexpected active selector implementation")
    source = source.replace(old, 'digitExperiment: "captcha-v3"')
    old = '$("test-dataset").textContent = letters ? "Official EMNIST Letters test" : "Official MNIST test";'
    if old not in source:
        raise ValueError("Unexpected active benchmark implementation")
    source = source.replace(old, '$("test-dataset").textContent = manifest.evaluation_label || (letters ? "Official EMNIST Letters test" : "Official MNIST test");')
    old = '$("digit-evaluation-link").href ='
    at = source.index(old)
    end = source.index(';', at)
    original_line = source[at:end + 1]
    source = source.replace(original_line, '$("digit-evaluation-link").href = manifest.evaluation_label ? "./evaluation/candidate-development.json" : `./evaluation/digits-${digitExperiment === "captcha-v3" ? "captcha-v3-preserved" : digitExperiment}.json`;\n'
                            '      $("benchmark-digits").querySelector("div > span > small").textContent = manifest.evaluation_label ? "MNIST validation · 5,000 examples" : "MNIST test · 10,000 examples";')
    app_path.write_text(source)
    catalog = PREVIEW / "v3/cnn-models.js"
    text = catalog.read_text().replace('name: "Preserved residual CNN · MNIST + synthetic data"', 'name: "64px CAPTCHA training extension · candidate preview"')
    text = text.replace('Previous default, preserved unchanged. Trained on MNIST and synthetic CAPTCHA-style examples; it is not MNIST-only.',
                        'Separate candidate trained on MNIST, EMNIST Digits and independent CAPTCHA-style data. Preview validation results only; reserved evaluation is separate.')
    text = text.replace('data: "MNIST + independent synthetic CAPTCHA-style examples"',
                        'data: "MNIST + EMNIST Digits + independently generated CAPTCHA-style examples"')
    catalog.write_text(text)
    html = PREVIEW / "index.html"
    html.write_text(html.read_text().replace("Preserved residual CNN · MNIST + synthetic data</option>", "64px training extension · candidate preview</option>"))
    write_json(PREVIEW / "evaluation/candidate-development.json", {"scope": "Candidate development only; reserved test and official follow-up NOT RUN",
               "model_sha256": manifest["sha256"], "selected_epoch": selection["selected_epoch"], "validation": metadata["validation"]})
    runtime = [PREVIEW / "index.html", *PREVIEW.glob("v3/*.js"), *PREVIEW.glob("v3/*.css"),
               folder / "weights.bin", folder / "manifest.json", folder / "parity.json", PREVIEW / "evaluation/candidate-development.json"]
    freeze = {"model_sha256": manifest["sha256"], "checkpoint_sha256": selection["checkpoint_sha256"],
              "files": {str(p.relative_to(PREVIEW)): digest(p) for p in runtime},
              "helper_sha256": digest(ROOT / "digitlab/captcha_extension_browser.py"),
              "development_report_sha256": selection["development_report_sha256"], "official_inputs_used": False,
              "frozen_utc": datetime.now(timezone.utc).isoformat(), "scope": "Isolated full-app candidate; active assets preserved"}
    with FREEZE.open("x") as stream:
        json.dump(freeze, stream, indent=2)
    print("PASS: selected candidate exported in isolated app; active models unchanged")


def collect(official=False):
    metadata, selection = selected()
    freeze = json.loads(FREEZE.read_text())
    verify_preview(freeze)
    if freeze["checkpoint_sha256"] != selection["checkpoint_sha256"]:
        raise ValueError("Wrong selected browser checkpoint")
    output = ROOT / "reports" / (NAME + ("-official-raw.json" if official else "-browser.json"))
    if output.exists():
        raise FileExistsError("Preserve completed browser collection")
    if official:
        prior = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
        if not metadata.get("independent_test_eligible") or prior["status"] != "PASS" or prior["checkpoint_sha256"] != selection["checkpoint_sha256"]:
            raise ValueError("Require matched passing browser and reserved gates before official images")
        paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    else:
        paths = sorted((DIRECTORY / "raw-fixtures").glob("sample-*.png"))[::9]
        if len(paths) != 60:
            raise ValueError("Require sixty predeclared development uploads")
    report = {"status": "FAIL", "checkpoint_sha256": selection["checkpoint_sha256"], "model_sha256": freeze["model_sha256"],
              "scope": "Official follow-up after prior exposure; no tuning" if official else "Actual isolated application parity on development data",
              "checks": {}, "requests": []}

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(PREVIEW)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("request", lambda r: report["requests"].append({"method": r.method, "url": r.url}))
            url = f"http://127.0.0.1:{server.server_port}/"
            page.goto(url)
            page.wait_for_function("window.digitLab?.state.ready && !digitLab.state.loading", timeout=60000)
            if page.evaluate("digitLab.state.model.manifest.sha256") != freeze["model_sha256"]:
                raise ValueError("Candidate is not the loaded model")
            fixture = json.loads((PREVIEW / "model/captcha-v3/digits/parity.json").read_text())
            if not official:
                parity = page.evaluate("""f=>f.cases.map(c=>{const r=digitLab.predict(c.input),delta=(a,b)=>Math.max(...Array.from(a,(v,i)=>Math.abs(v-b[i])));return {logits:delta(r.logits,c.logits),pool1:delta(r.first,c.pool1),pool2:delta(r.second,c.pool2),hidden:delta(r.hidden,c.hidden)};})""", fixture)
                if any(v > .0001 for row in parity for v in row.values()):
                    raise ValueError("Actual activation mismatch")
                times = page.evaluate("""input=>{digitLab.predict(input);return Array.from({length:30},()=>{const t=performance.now();digitLab.predict(input);return performance.now()-t;});}""", fixture["cases"][0]["input"])
                report.update(p95_ms=float(np.percentile(times,95)), median_ms=float(np.median(times)))
                if report["p95_ms"] >= POLICY["desktop_p95_limit_ms"]:
                    raise ValueError("Desktop speed gate failed")
                report["checks"]["activations"] = parity
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("n=>digitLab.state.uploads.length===n&&!digitLab.state.busy", arg=len(paths), timeout=120000)
            raw = page.evaluate("digitLab.exportRecord()")
            if any("error" in r or r["model_sha256"] != freeze["model_sha256"] or r["file"] != p.name for r,p in zip(raw["predictions"],paths)):
                raise ValueError("Upload identity/error mismatch")
            if official:
                report.update(raw=raw, input_sha256={p.name: digest(p) for p in paths}, comparison="NOT RUN; raw saved before reference labels")
            else:
                model = baseline_model()
                model.load_state_dict(torch.load(DIRECTORY / "best.pt", map_location="cpu", weights_only=True))
                model.eval()
                maximum = 0.
                for p,r in zip(paths,raw["predictions"]):
                    x = prepare(np.asarray(Image.open(p).convert("RGBA")),64)
                    np.testing.assert_allclose(x.flatten(),r["input"],atol=1e-6,rtol=0)
                    with torch.no_grad():
                        scores = model(torch.from_numpy(x[None])).softmax(1)[0].numpy()
                    np.testing.assert_allclose(scores,r["scores"],atol=1e-5,rtol=0)
                    maximum = max(maximum,float(np.max(np.abs(scores-r["scores"]))))
                report["checks"].update(upload_count=len(paths),maximum_score_error=maximum)
                page.evaluate("digitLab.activateMode('letters')")
                letters = json.loads((ROOT / "dist/model/robust/letters/parity.json").read_text())
                if page.evaluate("digitLab.state.model.manifest.sha256") != letters["model_sha256"]:
                    raise ValueError("Letter mode changed")
                error = page.evaluate("f=>Math.max(...f.cases.map(c=>{const r=digitLab.predict(c.input);return Math.max(...r.logits.map((v,i)=>Math.abs(v-c.logits[i])));}))", letters)
                if error > .0001:
                    raise ValueError("Letter activations mismatch")
                page.evaluate("digitLab.activateMode('words')")
                if not page.locator("#words-workspace").is_visible():
                    raise ValueError("Word mode unavailable")
                page.evaluate("digitLab.activateMode('digits')")
                if page.evaluate("digitLab.state.model.manifest.sha256") != freeze["model_sha256"]:
                    raise ValueError("Mode roundtrip lost candidate")
                report["checks"].update(letters_and_words="PASS",letter_max_logit_error=error)
                page.screenshot(path=str(ROOT / "reports/screenshots" / (NAME + "-preview.png")))
            if errors or any(r["method"] != "GET" or not r["url"].startswith((url,"blob:")) for r in report["requests"]):
                raise ValueError("Page error or non-static request")
            verify_preview(freeze)
            report.update(status="PASS",page_errors=errors,browser_version=browser.version)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        with output.open("x") as stream:
            json.dump(report,stream,indent=2)
    print("PASS:", "frozen official raw output" if official else "actual candidate browser parity/speed")


def compare():
    metadata, selection = selected()
    if not metadata.get("independent_test_eligible"):
        raise ValueError("No official comparison for an independently rejected model")
    output = ROOT / "reports" / (NAME + "-official-comparison.json")
    if output.exists():
        raise FileExistsError("Preserve completed official comparison")
    raw_path = ROOT / "reports" / (NAME + "-official-raw.json")
    raw_hash = digest(raw_path)
    raw = json.loads(raw_path.read_text())
    if raw["status"] != "PASS" or raw["checkpoint_sha256"] != selection["checkpoint_sha256"]:
        raise ValueError("Require passing frozen raw recording")
    for name,value in raw["input_sha256"].items():
        if digest(ROOT.parent / "Dia2/Desafio" / name) != value:
            raise ValueError("Input changed")
    reference = ROOT / "reports/captcha-v3-challenge-comparison.json"
    expected = {r["file"]: r["expected"] for r in json.loads(reference.read_text())["cases"]}
    result = evaluate(raw["raw"]["predictions"],expected)
    result.update(raw_sha256=raw_hash,reference_sha256=digest(reference),model_sha256=raw["model_sha256"],
                  scope="Single post-freeze follow-up after prior exposure; never model selection")
    with output.open("x") as stream:
        json.dump(result,stream,indent=2)
    if digest(raw_path) != raw_hash:
        raise ValueError("Raw recording changed")
    metadata["official_followup"] = {"correct":result["correct"],"correct_above_90":result["correct_above_90"],"accepted":result["accepted"],
                                     "raw_sha256":raw_hash,"comparison_sha256":digest(output)}
    write_json(REPORT,metadata)
    print(json.dumps(metadata["official_followup"]))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",choices=("export","qa","official","compare"),required=True)
    args=parser.parse_args()
    torch.set_num_threads(2)
    {"export":export,"qa":collect,"official":lambda:collect(True),"compare":compare}[args.stage]()


if __name__ == "__main__":
    main()
