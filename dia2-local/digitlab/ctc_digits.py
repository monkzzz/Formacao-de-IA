"""Independent single-digit CTC experiment using frozen pretrained CAPTCHA weights.

No official challenge images, filenames, labels or generator are used here.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from .ensemble_benchmark import render
from .train import ROOT


NAME = "ctc-digits-v1"
WEIGHTS = (0, .25, .5, .75, 1)
DEVELOPMENT_FONTS = ("arial.ttf", "times.ttf", "cour.ttf", "tahoma.ttf", "verdana.ttf")
TEST_FONTS = ("georgia.ttf", "cambria.ttc", "consola.ttf", "trebuc.ttf", "calibri.ttf")


def model_metadata():
    provenance = json.loads((ROOT / "reports/ddddocr-independent-development-20261016.json").read_text(encoding="utf-8"))["models"]
    charsets = json.loads((ROOT / "dist/v3/ddddocr-charsets.json").read_text(encoding="utf-8"))
    return {name: {**identity, "charset": charsets[name]} for name, identity in provenance.items()}


def restore_weights():
    from urllib.request import urlopen

    directory = ROOT / "artifacts/ddddocr-candidates"
    directory.mkdir(parents=True, exist_ok=True)
    for identity in model_metadata().values():
        path = directory / identity["file"]
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != identity["sha256"]:
                raise ValueError("Preserve and investigate mismatched model bytes: " + str(path))
            continue
        with urlopen(identity["url"], timeout=180) as response:
            data = response.read(identity["bytes"] + 1)
        if len(data) != identity["bytes"] or hashlib.sha256(data).hexdigest() != identity["sha256"]:
            raise ValueError("Downloaded model bytes do not match pinned provenance")
        with path.open("xb") as handle:
            handle.write(data)
        print("Restored verified " + path.name, flush=True)


def digit_log_probabilities(logits, charset):
    """Exact CTC likelihood for each one-character target, including all alignments."""
    logits = np.asarray(logits, dtype=np.float64).reshape(-1, len(charset))
    indices = [charset.index(str(digit)) for digit in range(10)]
    maximum = logits.max(axis=1, keepdims=True)
    log_probs = logits - maximum - np.log(np.exp(logits - maximum).sum(axis=1, keepdims=True))
    before = 0.0
    emitting = np.full(10, -np.inf)
    after = np.full(10, -np.inf)
    for row in log_probs:
        blank = row[0]
        before, emitting, after = (before + blank,
            np.logaddexp(before, emitting) + row[indices],
            np.logaddexp(emitting, after) + blank)
    return np.logaddexp(emitting, after)


def digit_scores(logits, charset):
    values = digit_log_probabilities(logits, charset)
    scores = np.exp(values - values.max())
    return scores / scores.sum()


def ctc_text(logits, charset):
    previous, text = 0, ""
    for index in np.asarray(logits).reshape(-1, len(charset)).argmax(axis=1):
        if index != previous and index:
            text += charset[index]
        previous = index
    return text


def metrics(scores, labels):
    return {"count": len(labels), "correct": int((scores.argmax(1) == labels).sum()),
            "accuracy": float((scores.argmax(1) == labels).mean()),
            "loss": float(-np.log(np.maximum(scores[np.arange(len(labels)), labels], 1e-15)).mean())}


def create_json(path, data):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)


def evaluate(stage):
    import onnxruntime as ort

    directory = ROOT / "artifacts/ddddocr-candidates"
    metadata = model_metadata()
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.log_severity_level = 3
    sessions = {}
    for name, identity in metadata.items():
        path = directory / identity["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == identity["sha256"]
        sessions[name] = ort.InferenceSession(str(path), options, providers=["CPUExecutionProvider"])
    seed = 2026101701 if stage == "development" else 2026101702
    rng = np.random.default_rng(seed)
    fonts = DEVELOPMENT_FONTS if stage == "development" else TEST_FONTS
    rows, vectors, labels = [], {name: [] for name in sessions}, []
    for i in range(1000):
        digit, severity = i % 10, 0 if i < 500 else 4
        image = render(rng, digit, None, Path("C:/Windows/Fonts") / fonts[(i // 10) % len(fonts)], severity)
        resized = image.convert("RGB").resize((int(image.width * 64 / image.height), 64), Image.Resampling.LANCZOS).convert("L")
        pixels = (np.asarray(resized).astype(np.float32) / 255 - .5) / .5
        row = {"index": i, "expected": digit, "severity": severity, "models": {}}
        for name, session in sessions.items():
            output = session.run(None, {session.get_inputs()[0].name: pixels[None, None]})[0]
            charset = metadata[name]["charset"]
            scores = digit_scores(output, charset)
            vectors[name].append(scores)
            row["models"][name] = {"raw_text": ctc_text(output, charset), "predicted": int(scores.argmax()), "scores": scores.tolist()}
        labels.append(digit)
        rows.append(row)
        if (i + 1) % 100 == 0:
            print(f"{stage}: {i+1}/1000", flush=True)
    return metadata, {name: np.array(values) for name, values in vectors.items()}, np.array(labels), rows, seed, fonts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("development", "test"))
    parser.add_argument("--restore-weights", action="store_true", help="Restore missing pinned public model files into ignored artifacts")
    args = parser.parse_args()
    if args.restore_weights:
        restore_weights()
    if not args.stage:
        if not args.restore_weights:
            parser.error("Provide --stage or --restore-weights")
        return
    protocol = ROOT / "reports" / (NAME + "-protocol.json")
    selection = ROOT / "reports" / (NAME + "-selection.json")
    destination = ROOT / "reports" / (NAME + "-" + args.stage + ".json")
    if destination.exists():
        raise SystemExit("Preserve completed experiments")
    if args.stage == "development":
        create_json(protocol, {"scope": "Fresh independent synthetic single-digit development/test experiment, not real CAPTCHA population accuracy",
            "development_seed": 2026101701, "test_seed": 2026101702, "count_per_stage": 1000,
            "weight_grid_current_model": WEIGHTS, "development_fonts": DEVELOPMENT_FONTS, "test_fonts": TEST_FONTS,
            "selection": "Maximum development accuracy, then minimum conditional log loss, then closest to equal weights",
            "decoding": "Exact full-vocabulary CTC likelihood of each single-digit target; conditional normalization across ten digits",
            "official_challenge_used": False})
    elif not selection.exists():
        raise SystemExit("Select using development data before the test")
    selected = json.loads(selection.read_text()) if args.stage == "test" else None
    metadata, vectors, labels, rows, seed, fonts = evaluate(args.stage)
    if args.stage == "development":
        candidates = []
        for weight in WEIGHTS:
            candidate = metrics(weight * vectors["ddddocr"] + (1-weight) * vectors["ddddocr-old"], labels)
            candidate["current_model_weight"] = weight
            candidates.append(candidate)
        best = min(candidates, key=lambda row: (-row["accuracy"], row["loss"], abs(row["current_model_weight"]-.5)))
        create_json(selection, {"name": NAME, "selected_before_test": True, "official_challenge_used": False,
            "decoding": "exact-single-digit-ctc-v1", "current_model_weight": best["current_model_weight"], "development": best,
            "models": {name: {k:v for k,v in identity.items() if k != "charset"} for name,identity in metadata.items()}})
        selected = best
    weight = selected["current_model_weight"]
    combined = weight * vectors["ddddocr"] + (1-weight) * vectors["ddddocr-old"]
    summary = {name: metrics(values, labels) for name,values in vectors.items()}
    summary["selected"] = metrics(combined, labels)
    greedy = {name: sum(row["models"][name]["raw_text"] == str(row["expected"]) for row in rows) for name in vectors}
    create_json(destination, {"name": NAME, "stage": args.stage, "seed": seed, "fonts": fonts,
        "official_challenge_used": False, "current_model_weight": weight, "summary": summary,
        "unrestricted_ctc_correct": greedy, "records": rows})
    print(json.dumps({"summary": summary, "unrestricted_ctc_correct": greedy, "current_model_weight": weight}, indent=2))


if __name__ == "__main__":
    main()
