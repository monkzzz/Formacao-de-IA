"""Freeze and evaluate pretrained CAPTCHA readers in the local browser; never tune on official images."""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import io
import json

from .platform_support import font_root, resolve_fonts

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

from .ensemble_benchmark import render
from .qa import open_browser
from .train import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("synthetic", "challenge", "download-smoke"), required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8782/")
    parser.add_argument("--report-prefix", required=True)
    parser.add_argument("--cached-weights", action="store_true", help="Serve previously verified candidate weights through browser interception")
    parser.add_argument("--readers", nargs="+", choices=("ddddocr", "ddddocr-old", "captcha-digits"), default=["ddddocr", "ddddocr-old"])
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--seed", type=int, default=2026101611)
    parser.add_argument("--noise", type=int, default=2)
    parser.add_argument("--native-parity", action="store_true", help="Compare conditional browser scores with native ONNX Runtime on identical prepared pixels")
    args = parser.parse_args()
    if args.count < 1 or args.noise < 0:
        parser.error("Synthetic count must be positive and noise nonnegative")
    if args.stage == "challenge" and not args.url.startswith("http://127.0.0.1:"):
        parser.error("Official evaluation images must stay in the local browser")
    prefix = args.report_prefix
    report = ROOT / "reports" / (prefix + ".json")
    freeze = ROOT / "reports" / (prefix + "-freeze.json")
    raw_paths = [ROOT / "reports" / (prefix + "-" + reader + "-raw.json") for reader in args.readers]
    if any(path.exists() for path in [report, freeze, *raw_paths]):
        parser.error("Use a new report prefix to preserve existing evidence")
    sources = {path.relative_to(ROOT).as_posix(): digest(path) for path in
               [ROOT / "dist/index.html", *sorted((ROOT / "dist/v3").glob("*.js")), ROOT / "dist/v3/ddddocr-charsets.json"]}
    scope = ("Known official challenge follow-up, not a blind test; no model selection or further tuning"
             if args.stage == "challenge" else "Fresh synthetic browser integration screening, not real CAPTCHA population accuracy")
    create_json(freeze, {"frozen_at": datetime.now(timezone.utc).isoformat(), "stage": args.stage,
        "sources": sources, "scope": scope, "readers": args.readers,
        "synthetic_count": args.count, "synthetic_seed": args.seed, "synthetic_noise": args.noise,
        "selection": "Both models selected using independent synthetic development before official evaluation",
        "further_tuning_permitted": args.stage != "challenge", "cached_weights": args.cached_weights})
    labels = {}
    if args.stage == "challenge":
        paths = [ROOT.parent / "Dia2/Desafio" / f"caso_{i:02d}.png" for i in range(1, 11)]
    else:
        directory = ROOT / "artifacts/ddddocr-candidates" / prefix
        directory.mkdir(parents=True, exist_ok=False)
        rng = np.random.default_rng(args.seed)
        fonts = resolve_fonts(font_root(), ("arial.ttf", "times.ttf", "cour.ttf", "tahoma.ttf", "verdana.ttf"))
        count = args.count if args.stage == "synthetic" else 1
        paths = []
        for i in range(count):
            image = render(rng, i % 10, None, fonts[(i // 10) % len(fonts)], 0 if i < max(1, count // 2) else args.noise)
            path = directory / f"sample-{i:03d}.png"
            image.save(path)
            paths.append(path)
            labels[path.name] = i % 10
    results = []
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        for reader, raw_path in zip(args.readers, raw_paths):
            print("START " + reader, flush=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            errors, requests = [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.context.on("request", lambda request: requests.append({"method": request.method, "url": request.url,
                "has_body": request.post_data is not None}))

            def guard(route):
                request = route.request
                if request.method != "GET" or request.post_data is not None:
                    route.abort()
                elif args.cached_weights and request.url.startswith("https://raw.githubusercontent.com/sml2h3/ddddocr/"):
                    name = request.url.rsplit("/", 1)[-1]
                    if name not in ("common.onnx", "common_old.onnx"):
                        route.abort()
                    else:
                        route.fulfill(path=str(ROOT / "artifacts/ddddocr-candidates" / name),
                            content_type="application/octet-stream", headers={"Access-Control-Allow-Origin": "*"})
                else:
                    route.continue_()
            page.context.route("**/*", guard)
            page.goto(args.url)
            page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
            page.locator("#digit-reader").select_option(reader)
            assert page.locator("#digit-quality-options").is_hidden()
            assert page.locator("#scores").is_hidden() and page.locator("#network").is_hidden()
            page.locator("#files").set_input_files([str(path) for path in paths])
            page.wait_for_function("n => digitLab.state.uploads.length === n && !digitLab.state.busy", arg=len(paths), timeout=600000)
            raw = page.evaluate("digitLab.exportRecord()")
            assert [row["file"] for row in raw["predictions"]] == [path.name for path in paths]
            if args.native_parity and reader == "captcha-digits":
                import onnxruntime as ort
                from .ctc_digits import digit_scores

                png = page.locator("#digit-ocr-preview").get_attribute("src").split(",", 1)[1]
                image = Image.open(io.BytesIO(base64.b64decode(png))).convert("L")
                pixels = ((np.asarray(image).astype(np.float64) / 255 - .5) / .5).astype(np.float32)
                options = ort.SessionOptions()
                options.intra_op_num_threads = 2
                options.log_severity_level = 3
                session = ort.InferenceSession(str(ROOT / "artifacts/ddddocr-candidates/common_old.onnx"),
                    options, providers=["CPUExecutionProvider"])
                logits = session.run(None, {session.get_inputs()[0].name: pixels[None, None]})[0]
                charset = json.loads((ROOT / "dist/v3/ddddocr-charsets.json").read_text(encoding="utf-8"))["ddddocr-old"]
                expected_scores = digit_scores(logits, charset)
                actual_scores = np.array(raw["predictions"][-1]["scores"])
                delta = float(np.max(np.abs(expected_scores - actual_scores)))
                assert delta <= .00001, delta
                raw["native_conditional_score_max_delta"] = delta
            if reader == "captcha-digits" and args.stage != "challenge":
                page.locator("#drawing").evaluate("""canvas => {
                  const ctx=canvas.getContext('2d');ctx.fillStyle='#14251d';ctx.fillRect(0,0,canvas.width,canvas.height);
                  ctx.fillStyle='white';ctx.font='220px Arial';ctx.textAlign='center';ctx.textBaseline='middle';
                  ctx.fillText('7',canvas.width/2,canvas.height/2);
                }""")
                page.locator("#classify").click()
                page.wait_for_function("!digitLab.state.busy", timeout=60000)
                predicted = page.locator("#predicted").inner_text()
                assert predicted == "7", predicted
                raw["real_drawing_smoke"] = {"expected": "7", "predicted": predicted,
                    "score_display": page.locator("#confidence").inner_text(), "scope": "One generated drawing, not an accuracy benchmark"}
            raw.update({"scope": scope, "url": args.url, "freeze_sha256": digest(freeze), "page_errors": errors,
                        "request_methods": sorted(set(row["method"] for row in requests)),
                        "request_body_count": sum(row["has_body"] for row in requests),
                        "input_file_sha256": {path.name: digest(path) for path in paths}})
            create_json(raw_path, raw)
            screenshot = ROOT / "reports/screenshots" / (prefix + "-" + reader + ".png")
            screenshot.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(screenshot), full_page=True)
            results.append((reader, raw_path, raw))
            print(f"SAVED {reader}: {len(raw['predictions'])} outputs", flush=True)
            page.close()
        browser.close()
    assert all(digest(ROOT / name) == value for name, value in sources.items())
    if args.stage == "challenge":
        # Compare only after both complete output sets have been saved durably.
        comparison = json.loads((ROOT / "reports/challenge-comparison.json").read_text(encoding="utf-8"))
        labels = {row["file"]: row["expected"] for row in comparison["cases"]}
    models = []
    for reader, raw_path, raw in results:
        cases = [{"file": row["file"], "expected": labels[row["file"]], "predicted": row.get("predicted"),
                  "raw_text": row.get("raw_text"), "correct": row.get("predicted") == labels[row["file"]],
                  "error": row.get("error")} for row in raw["predictions"]]
        models.append({"reader": reader, "correct": sum(row["correct"] for row in cases), "count": len(cases),
            "raw_report": raw_path.name, "raw_sha256": digest(raw_path), "cases": cases,
            "errors": sum(bool(row["error"]) for row in cases), "page_errors": raw["page_errors"],
            "request_body_count": raw["request_body_count"], "request_methods": raw["request_methods"]})
    status = "PASS" if all(not model["errors"] and not model["page_errors"] and not model["request_body_count"] and
                           model["request_methods"] == ["GET"] for model in models) else "FAIL"
    create_json(report, {"status": status, "scope": scope, "models": models,
                        "sources_unchanged": True, "application_version": raw["application_version"]})
    print(json.dumps({"status": status, "models": [{k: model[k] for k in ("reader", "correct", "count", "errors")} for model in models]}, indent=2))


if __name__ == "__main__":
    main()
