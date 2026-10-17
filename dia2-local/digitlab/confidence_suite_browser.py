"""Isolated preview, real browser parity and one frozen official follow-up."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import tempfile
import threading

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import torch

from .confidence_suite import (DEEP_ARCHITECTURE, DIRECTORY, NAME, POLICY, REPORT,
                               DeeperResidualCNN, baseline_model, digest, load_selection, read_set)
from .highres import export
from .preprocess import prepare
from .qa import open_browser
from .residual import ARCHITECTURE
from .train import ROOT, write_json

PREVIEW = ROOT / ".tmp" / NAME


def replace_one(source, before, after):
    if source.count(before) != 1:
        raise ValueError(f"Unexpected runtime source around: {before[:80]}")
    return source.replace(before, after, 1)


def patch_runtime(preview):
    """Patch only a new isolated copy; preserve both baseline and deep contracts."""
    folder = preview / "v3"
    path = folder / "residual.js"
    source = replace_one(path.read_text(), "[16, 32].flatMap", "[16, 32, 16, 32].flatMap")
    path.write_text(source)
    path = folder / "inference.js"
    source = path.read_text()
    for prefix in ("", "model."):
        before = f'const residual = {prefix}manifest.architecture === "{ARCHITECTURE}";'
        after = (f'const deep = {prefix}manifest.architecture === "{DEEP_ARCHITECTURE}";\n'
                 f'  const residual = deep || {prefix}manifest.architecture === "{ARCHITECTURE}";')
        source = replace_one(source, before, after)
    source = replace_one(source,
                         '["cnn16-32-128", "cnn64-16-32-128", "residual64-16-32-128"]',
                         f'["cnn16-32-128", "cnn64-16-32-128", "residual64-16-32-128", "{DEEP_ARCHITECTURE}"]')
    source = replace_one(source, "...(residual ? RESIDUAL_SHAPES : {})",
                         '...(residual ? Object.fromEntries(Object.entries(RESIDUAL_SHAPES).filter(([key]) => deep || (!key.startsWith("block3.") && !key.startsWith("block4.")))) : {})')
    source = replace_one(source,
                         'if (residual) first = residualBlock(first, 32, 16, w, "block1", convRelu);',
                         'if (residual) first = residualBlock(first, 32, 16, w, "block1", convRelu);\n  if (deep) first = residualBlock(first, 32, 16, w, "block3", convRelu);')
    source = replace_one(source,
                         'if (residual) second = residualBlock(second, 8, 32, w, "block2", convRelu);',
                         'if (residual) second = residualBlock(second, 8, 32, w, "block2", convRelu);\n  if (deep) second = residualBlock(second, 8, 32, w, "block4", convRelu);')
    path.write_text(source)
    path = folder / "app.js"
    if path.exists():
        source = path.read_text()
        source = replace_one(source,
                             '$("architecture").textContent = manifest.architecture === "residual64-16-32-128"',
                             f'$("architecture").textContent = manifest.architecture === "{DEEP_ARCHITECTURE}"\n'
                             '      ? "64px · Conv 16 → Residual 16 ×2 → Conv 32 → Average pool → Residual 32 ×2 → Dense 128 → 10"\n'
                             '      : manifest.architecture === "residual64-16-32-128"')
        source = replace_one(source,
                             'letters ? "Official EMNIST Letters test" : "Official MNIST test"',
                             'letters ? "Official EMNIST Letters test" : "Clean validation · candidate preview"')
        path.write_text(source)


def core_files(preview):
    return {str(p.relative_to(preview)): digest(p) for p in
            [preview / "index.html", *sorted((preview / "v3").glob("*.js"))]}


def parity(page, fixture, expression):
    result = page.evaluate("""({fixture, expression}) => {
      const run = new Function('input', expression);
      const error = (a,b) => Math.max(...Array.from(a,(x,i)=>Math.abs(x-b[i])));
      return fixture.cases.map(c => {
        const p=run(c.input);
        return {logits:error(p.logits,c.logits),hidden:error(p.hidden,c.hidden),
          first:error(p.first,c.pool1),second:error(p.second,c.pool2)};
      });
    }""", {"fixture": fixture, "expression": expression})
    if any(value > fixture["absolute_tolerance"] for row in result for value in row.values()):
        raise ValueError(f"Browser/Python parity failed: {result}")
    return result


def self_test(deep=True):
    """Actually execute the extra blocks on nonidentity fixture weights in Chromium."""
    report_path = ROOT / "reports" / (NAME + ("-runtime-self-test.json" if deep else "-baseline-runtime-self-test.json"))
    if report_path.exists():
        raise FileExistsError(report_path)
    with tempfile.TemporaryDirectory(dir=ROOT / ".tmp", prefix="consistency-runtime-") as temporary:
        preview = Path(temporary)
        (preview / "v3").mkdir()
        for name in ("inference.js", "preprocess.js", "residual.js"):
            shutil.copy2(ROOT / "dist/v3" / name, preview / "v3" / name)
        patch_runtime(preview)
        model = DeeperResidualCNN() if deep else baseline_model()
        if deep:
            model.load_state_dict(baseline_model().state_dict(), strict=False)
        # Nonzero extra blocks ensure this tests their execution, not just identity.
        with torch.no_grad():
            for block in ((model.block3, model.block4) if deep else ()):
                block.expand.weight.normal_(0, .02)
                block.expand.bias.normal_(0, .01)
        inputs = torch.rand(3, 1, 64, 64)
        manifest = export(model, preview / "model/captcha-v3/digits", {"scope": "Nonidentity deep runtime math fixture"}, inputs)
        manifest["architecture"] = DEEP_ARCHITECTURE if deep else ARCHITECTURE
        write_json(preview / "model/captcha-v3/digits/manifest.json", manifest)
        (preview / "index.html").write_text('''<!doctype html><title>Deep runtime math fixture</title>
<script type="module">import {loadModel,predict} from './v3/inference.js';
window.fixtureModel=await loadModel();window.fixturePredict=input=>predict(window.fixtureModel,input);</script>''')
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(preview)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = open_browser(playwright)
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{server.server_port}/")
                page.wait_for_function("typeof window.fixturePredict === 'function'", timeout=60000)
                fixture = json.loads((preview / "model/captcha-v3/digits/parity.json").read_text())
                checks = parity(page, fixture, "return window.fixturePredict(input)")
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    write_json(report_path, {"status": "PASS", "scope": "Real Chromium/Python math parity; three random inputs, no training/test/challenge samples; extra blocks nonidentity when deep",
                             "checks": checks, "architecture": DEEP_ARCHITECTURE if deep else ARCHITECTURE})
    print("PASS: actual browser logits and activations", "deep" if deep else "baseline")


def export_preview():
    metadata, selection, model = load_selection()
    if PREVIEW.exists() or (DIRECTORY / "runtime-freeze.json").exists():
        raise FileExistsError("Preserve prior preview/freeze")
    runtime_test = json.loads((ROOT / "reports" / (NAME + "-runtime-self-test.json")).read_text())
    if runtime_test["status"] != "PASS":
        raise ValueError("Deep runtime must pass the independent math self-test")
    if json.loads((ROOT / "reports" / (NAME + "-baseline-runtime-self-test.json")).read_text())["status"] != "PASS":
        raise ValueError("Extended runtime must also preserve baseline math")
    development = read_set("development", metadata)
    inputs = development["views"][:10, 0]
    training = {"test": metadata["arms"][selection["arm"]]["validation"]["clean"],
                "split": {"train": 55000, "validation": 5000},
                "scope": "Development validation only; reserved test NOT RUN", "policy": POLICY,
                "arm": selection["arm"], "epoch": selection["selected_epoch"]}
    folder = DIRECTORY / "browser-export"
    manifest = export(model, folder, training, inputs)
    manifest["architecture"] = DEEP_ARCHITECTURE if selection["arm"] == "capacity" else ARCHITECTURE
    write_json(folder / "manifest.json", manifest)
    shutil.copytree(ROOT / "dist", PREVIEW, ignore=shutil.ignore_patterns("*.sfc", "roms"))
    model_folder = PREVIEW / "model/captcha-v3/digits"
    for name in ("weights.bin", "manifest.json", "parity.json"):
        shutil.copy2(folder / name, model_folder / name)
    patch_runtime(PREVIEW)
    index = PREVIEW / "index.html"
    index.write_text(re.sub(r"<title>.*?</title>", "<title>Digit Lab · local candidate preview</title>", index.read_text(), count=1))
    freeze = {"checkpoint_sha256": selection["checkpoint_sha256"], "model_sha256": manifest["sha256"],
              "arm": selection["arm"], "architecture": manifest["architecture"],
              "runtime_sha256": core_files(PREVIEW), "manifest_sha256": digest(model_folder / "manifest.json"),
              "official_inputs_used": False, "preview_only": True,
              "source_sha256": digest(Path(__file__))}
    with (DIRECTORY / "runtime-freeze.json").open("x") as stream:
        json.dump(freeze, stream, indent=2)
    print("PASS: isolated candidate preview frozen; active assets unchanged")


def check_preview(freeze):
    if (core_files(PREVIEW) != freeze["runtime_sha256"]
            or digest(PREVIEW / "model/captcha-v3/digits/manifest.json") != freeze["manifest_sha256"]
            or digest(PREVIEW / "model/captcha-v3/digits/weights.bin") != freeze["model_sha256"]
            or digest(Path(__file__)) != freeze["source_sha256"]):
        raise ValueError("Frozen preview/runtime changed")


def browser_check(url, official=False):
    metadata, selection, model = load_selection()
    if not url.startswith("http://127.0.0.1:"):
        raise ValueError("Use the isolated loopback preview")
    freeze = json.loads((DIRECTORY / "runtime-freeze.json").read_text())
    check_preview(freeze)
    output = ROOT / "reports" / (NAME + ("-official-raw.json" if official else "-browser.json"))
    if output.exists():
        raise FileExistsError(output)
    if official and not metadata.get("independent_test_eligible"):
        raise ValueError("Official follow-up requires a passed reserved test")
    report = {"status": "FAIL", "url": url, "checkpoint_sha256": selection["checkpoint_sha256"],
              "model_sha256": freeze["model_sha256"], "checks": {}, "requests": []}
    try:
        with sync_playwright() as playwright:
            browser = open_browser(playwright)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: report["requests"].append({"url": request.url, "method": request.method}))
            page.goto(url)
            page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
            if page.evaluate("digitLab.state.model.manifest.sha256") != freeze["model_sha256"]:
                raise ValueError("Preview served a different model")
            if official:
                prior = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
                if prior["status"] != "PASS" or prior["checkpoint_sha256"] != selection["checkpoint_sha256"]:
                    raise ValueError("Require matched browser QA before official follow-up")
                paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
            else:
                fixture = json.loads((PREVIEW / "model/captcha-v3/digits/parity.json").read_text())
                report["checks"]["activation_parity"] = parity(page, fixture, "return digitLab.predict(input)")
                paths = sorted((DIRECTORY / "development-fixtures").glob("*-raw.png"))
                timings = page.evaluate("""cases => {
                  for(let i=0;i<5;i++)digitLab.predict(cases[i%cases.length].input);
                  return Array.from({length:30},(_,i)=>{let start=performance.now();
                    digitLab.predict(cases[i%cases.length].input);return performance.now()-start;});
                }""", fixture["cases"])
                report["latency_p95_ms"] = float(np.quantile(timings, .95))
                report["latency_samples_ms"] = timings
                if report["latency_p95_ms"] >= POLICY["desktop_p95_limit_ms"]:
                    raise ValueError("Browser speed gate failed")
            page.locator("#files").set_input_files([str(p) for p in paths])
            page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=len(paths), timeout=120000)
            raw = page.evaluate("digitLab.exportRecord()")
            if len(raw["predictions"]) != len(paths):
                raise ValueError("Missing upload predictions")
            if official:
                report["raw"] = raw
                report["input_sha256"] = {p.name: digest(p) for p in paths}
                report["scope"] = "Single frozen official follow-up after prior exposure; raw saved before separate comparison; never used for selection"
            else:
                prepared = np.stack([prepare(np.asarray(Image.open(p).convert("RGBA")), 64) for p in paths])
                model.eval()
                with torch.no_grad():
                    scores = model(torch.from_numpy(prepared)).softmax(1).numpy()
                for i, record in enumerate(raw["predictions"]):
                    if record["file"] != paths[i].name:
                        raise ValueError("Upload order/identity mismatch")
                    np.testing.assert_allclose(record["input"], prepared[i].flatten(), atol=1e-6, rtol=0)
                    np.testing.assert_allclose(record["scores"], scores[i], atol=1e-5, rtol=0)
                report["checks"]["upload_parity_count"] = len(paths)
                report["architecture_label"] = page.locator("#architecture").inner_text()
                await_mode = "async mode => {await digitLab.activateMode(mode); return digitLab.state.model.manifest.sha256;}"
                letters_hash = page.evaluate(await_mode, "letters")
                letter_folder = PREVIEW / "model/robust/letters"
                letter_manifest = json.loads((letter_folder / "manifest.json").read_text())
                if letters_hash != letter_manifest["sha256"]:
                    raise ValueError("Letter model identity changed in the preview")
                letter_fixture = json.loads((letter_folder / "parity.json").read_text())
                report["checks"]["preserved_letter_activation_parity"] = parity(
                    page, letter_fixture, "return digitLab.predict(input)")
                if page.evaluate(await_mode, "digits") != freeze["model_sha256"]:
                    raise ValueError("Switching modes failed to restore the candidate")
                page.screenshot(path=str(ROOT / "reports/screenshots" / (NAME + "-preview.png")))
            if errors:
                raise ValueError(errors)
            if not all(r["method"] == "GET" and (r["url"].startswith(url) or r["url"].startswith("blob:"))
                       for r in report["requests"]):
                raise ValueError("Unexpected network request")
            report["checks"]["browser_only_inference"] = True
            report["status"] = "PASS"
            browser.close()
    finally:
        with output.open("x") as stream:
            json.dump(report, stream, indent=2)
    print(f"PASS: {'official raw follow-up' if official else 'candidate browser parity/speed'}")


def compare_predictions(records, expected):
    """Pure post-recording comparison; never used by rendering/training/inference."""
    if len(records) != len(expected) or len({row["file"] for row in records}) != len(records):
        raise ValueError("Missing or duplicate prediction records")
    if {row["file"] for row in records} != set(expected):
        raise ValueError("Prediction and reference identities differ")
    cases = []
    for row in records:
        scores = np.asarray(row["scores"], dtype=np.float64)
        if (scores.shape != (10,) or not np.isfinite(scores).all() or (scores < 0).any()
                or not np.isclose(scores.sum(), 1., atol=1e-5)):
            raise ValueError("Invalid raw score vector")
        predicted = int(scores.argmax())
        if predicted != row["predicted"]:
            raise ValueError("Recorded prediction disagrees with raw score argmax")
        label = expected[row["file"]]
        if not isinstance(label, int) or not 0 <= label < 10:
            raise ValueError("Invalid reference class")
        cases.append({"file": row["file"], "expected": label, "predicted": predicted,
                      "correct": predicted == label, "top_score": float(scores.max()),
                      "expected_class_score": float(scores[label]),
                      "correct_at_90": bool(predicted == label and scores[label] >= .9)})
    return {"count": len(cases), "correct": sum(row["correct"] for row in cases),
            "correct_at_90": sum(row["correct_at_90"] for row in cases),
            "target_met": bool(cases) and all(row["correct_at_90"] for row in cases), "cases": cases}


def compare_official():
    metadata, selection, _ = load_selection()
    if not metadata.get("independent_test_eligible"):
        raise ValueError("No official comparison for an ineligible candidate")
    raw_path = ROOT / "reports" / (NAME + "-official-raw.json")
    output = ROOT / "reports" / (NAME + "-official-comparison.json")
    if output.exists():
        raise FileExistsError("Preserve completed official comparison")
    raw_hash = digest(raw_path)
    raw = json.loads(raw_path.read_text())
    if raw["status"] != "PASS" or raw["checkpoint_sha256"] != selection["checkpoint_sha256"]:
        raise ValueError("Require a completed matched raw export before consulting reference labels")
    for name, checksum in raw["input_sha256"].items():
        if digest(ROOT.parent / "Dia2/Desafio" / name) != checksum:
            raise ValueError("Official input changed after recording")
    # This file is opened only here, after immutable raw predictions exist.
    reference = ROOT / "reports/captcha-v3-challenge-comparison.json"
    reference_cases = json.loads(reference.read_text())["cases"]
    expected = {row["file"]: row["expected"] for row in reference_cases}
    if len(expected) != 10:
        raise ValueError("Require the preserved ten-case reference comparison")
    result = {**compare_predictions(raw["raw"]["predictions"], expected), "raw_sha256": raw_hash,
              "reference_sha256": digest(reference), "checkpoint_sha256": selection["checkpoint_sha256"],
              "model_sha256": raw["model_sha256"],
              "scope": "One post-freeze official follow-up after prior exposure; never selects another model; no calibrated-probability claim"}
    with output.open("x") as stream:
        json.dump(result, stream, indent=2)
    if digest(raw_path) != raw_hash:
        raise ValueError("Raw export changed during comparison")
    metadata["official_followup"] = {"comparison_sha256": digest(output), "raw_sha256": raw_hash,
                                     "correct": result["correct"], "correct_at_90": result["correct_at_90"],
                                     "target_met": result["target_met"]}
    metadata["status"] = ("PASS: frozen official confidence target met; publication NOT RUN" if result["target_met"]
                          else "OFFICIAL FOLLOW-UP COMPLETE: confidence target NOT MET; baseline retained")
    write_json(REPORT, metadata)
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("self-test", "baseline-self-test", "export", "qa", "official", "compare"), required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8881/")
    args = parser.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(2026101909)
    if args.stage == "self-test":
        self_test()
    elif args.stage == "baseline-self-test":
        self_test(deep=False)
    elif args.stage == "export":
        export_preview()
    elif args.stage == "compare":
        compare_official()
    else:
        browser_check(args.url, official=args.stage == "official")


if __name__ == "__main__":
    main()
