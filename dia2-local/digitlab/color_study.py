"""One frozen RGB contrast comparison on independent development fixtures."""

import argparse
from datetime import datetime, timezone
import json
import math

import numpy as np
from PIL import Image
import torch

from .captcha_extension import baseline_model
from .color_preprocess import prepare_color
from .confidence import score_metrics
from .confidence_broad import font_groups
from .data import load_partition, split_indices
from .highres import render_broad
from .preprocess import prepare
from .preprocessing_study import digest
from .preprocessing_variants import foreground
from .train import ROOT, write_json

NAME = "color-preprocessing-v1"
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
SEED = 2026102301
PALETTES = (((220, 40, 40), (40, 100, 203)),
            ((40, 200, 40), (220, 90, 133)),
            ((253, 230, 138), (91, 33, 182)))
SOURCES = ("color_study.py", "color_preprocess.py", "color_preprocess.js", "preprocess.py",
           "preprocessing_variants.py", "highres.py", "captcha.py", "residual.py",
           "captcha_extension.py", "confidence.py", "confidence_broad.py", "data.py", "train.py")
POLICY = {"seed": SEED, "legacy_count": 1200, "color_count": 600, "clean_count": 5000,
          "accuracy_loss_tolerance": .001, "minimum_strict_90_gain": .005,
          "brier_tolerance": .001, "ece_tolerance": .005, "desktop_p95_limit_ms": 150,
          "official_or_reserved_inputs_used": False, "training": False,
          "scope": "Development only; new rendering seeds and historical source/font/model exposure",
          "selection": "Single candidate; all preservation/confidence gates required",
          "rejection_penalty": "Incorrect, score zero; uniform vector only for NLL/Brier"}


def verify(metadata):
    for path, value in metadata["frozen_sha256"].items():
        if digest(ROOT / path) != value:
            raise ValueError("Frozen identity changed: " + path)


def measure(model, images, labels, preparation):
    model.eval()
    tensors, rejected = [], []
    for i, image in enumerate(images):
        try:
            tensors.append(preparation(np.asarray(image), 64))
        except ValueError:
            tensors.append(np.zeros((1, 64, 64), np.float32))
            rejected.append(i)
    x = torch.from_numpy(np.stack(tensors))
    with torch.no_grad():
        scores = torch.cat([model(b).softmax(1) for b in x.split(128)]).numpy()
    failed = np.zeros(len(labels), bool)
    failed[rejected] = True
    scores[failed] = .1  # Explicit penalty, not an emitted prediction.
    return metrics(scores, labels, failed), scores, failed


def metrics(scores, labels, failed):
    result = score_metrics(scores, labels)
    predicted = scores.argmax(1).copy()
    predicted[failed] = -1
    correct = predicted == labels
    confidence = scores.max(1).copy()
    confidence[failed] = 0
    high = confidence > .9
    matrix = np.zeros((10, 11), dtype=int)
    for label, prediction in zip(labels, predicted):
        matrix[label, 10 if prediction < 0 else prediction] += 1
    ece = 0.
    bins = np.minimum((confidence * 10).astype(int), 9)
    for index in range(10):
        selected = bins == index
        if selected.any():
            ece += selected.mean() * abs(correct[selected].mean() - confidence[selected].mean())
    # Remove historical >=90 fields: this experiment uses strictly >90 only.
    result = {k: v for k, v in result.items() if "90" not in k}
    result.update(correct=int(correct.sum()), accuracy=float(correct.mean()), rejected=int(failed.sum()),
                  correct_above_90_count=int((correct & high).sum()),
                  correct_above_90_fraction=float((correct & high).mean()),
                  wrong_above_90_count=int((~correct & high).sum()), ece_10_bins=float(ece),
                  confusion_matrix_with_rejection=matrix.tolist())
    result.pop("confusion_matrix", None)
    return result


def gates(candidate, baseline):
    c, b = candidate["raw"], baseline["raw"]
    return {"no_more_rejections": c["rejected"] <= b["rejected"] and candidate["clean"]["rejected"] <= baseline["clean"]["rejected"],
            "raw_accuracy": c["accuracy"] >= b["accuracy"] - .001,
            "legacy_accuracy": candidate["legacy"]["accuracy"] >= baseline["legacy"]["accuracy"] - .001,
            "clean_accuracy": candidate["clean"]["accuracy"] >= baseline["clean"]["accuracy"] - .001,
            "strict_90_gain": c["correct_above_90_count"] - b["correct_above_90_count"] >= math.ceil(.005 * c["count"]),
            "lower_nll": c["loss"] < b["loss"], "brier": c["brier"] <= b["brier"] + .001,
            "ece": c["ece_10_bins"] <= b["ece_10_bins"] + .005,
            "confident_errors": c["wrong_above_90_count"] <= b["wrong_above_90_count"]}


def run():
    if DIRECTORY.exists() or REPORT.exists():
        raise FileExistsError("Preserve completed color study")
    DIRECTORY.mkdir(parents=True)
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    fonts = font_groups(ROOT / "data/open-fonts")["development"]
    paths = [ROOT / "digitlab" / n for n in SOURCES]
    paths += [ROOT / "docs/color-preprocessing.md", *fonts, *ROOT.glob("dist/v3/*"), ROOT / "dist/index.html"]
    paths += [p for p in (ROOT / "dist/model").rglob("*") if p.is_file() and p.name in ("weights.bin", "manifest.json")]
    paths += [ROOT.parent / "Dia2/Dataset-MNIST/data" / n for n in ("train-images-idx3-ubyte.gz", "train-labels-idx1-ubyte.gz")]
    metadata = {"status": "RUNNING", "policy": POLICY, "palettes": PALETTES,
                "started_utc": datetime.now(timezone.utc).isoformat(), "results": {},
                "frozen_sha256": {str(p.relative_to(ROOT, walk_up=True)): digest(p) for p in paths if p.is_file()}}
    write_json(REPORT, metadata)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    train, validation = split_indices(labels)
    np.savez(DIRECTORY / "source-split.npz", train=train, validation=validation)
    by_class = [validation[labels[validation] == d] for d in range(10)]
    rng = np.random.default_rng(SEED)
    raw, records = [], []
    fixtures = DIRECTORY / "fixtures"
    fixtures.mkdir()
    for i in range(1800):
        digit, printed = i % 10, (i // 10) % 2 == 0
        source = int(rng.choice(by_class[digit]))
        font = fonts[int(rng.integers(len(fonts)))]
        image = render_broad(rng, digit, None if printed else images[source], font)
        palette = None
        if i >= 1200:
            palette = ((i - 1200) // 20) % 3
            mask = foreground(np.asarray(image))[:, :, None]
            background, ink = (np.asarray(c) for c in PALETTES[palette])
            pixels = np.floor(background * (1 - mask) + ink * mask + .5).clip(0, 255).astype(np.uint8)
            image = Image.fromarray(pixels).convert("RGBA")
        path = fixtures / f"sample-{i:04d}.png"
        image.save(path)
        raw.append(image)
        records.append({"file": path.name, "label": digit, "printed": printed,
                        "source_index": None if printed else source, "font": str(font.relative_to(ROOT)),
                        "palette": palette, "group": "legacy" if i < 1200 else "color", "sha256": digest(path)})
    write_json(DIRECTORY / "records.json", records)
    clean = [Image.fromarray(images[i]).convert("RGBA") for i in validation]
    raw_labels = np.asarray([r["label"] for r in records])
    clean_labels = labels[validation].astype(np.int64)
    vectors = {"raw_labels": raw_labels, "clean_labels": clean_labels}
    model = baseline_model()
    for name, preparation in (("current", prepare), ("rgb", prepare_color)):
        result = {}
        for group, samples, targets in (("raw", raw, raw_labels), ("clean", clean, clean_labels)):
            result[group], scores, failed = measure(model, samples, targets, preparation)
            vectors[name + "_" + group] = scores
            vectors[name + "_" + group + "_rejected"] = failed
            if group == "raw":
                for subset, indices in (("legacy", np.arange(1200)), ("color", np.arange(1200, 1800)),
                                        *(("palette_" + str(p), np.array([i for i, r in enumerate(records) if r["palette"] == p])) for p in range(3))):
                    result[subset] = metrics(scores[indices], targets[indices], failed[indices])
        metadata["results"][name] = result
        write_json(REPORT, metadata)
        print(f"{name}: raw={result['raw']['accuracy']:.3%}, correct >90={result['raw']['correct_above_90_fraction']:.3%}, legacy={result['legacy']['accuracy']:.3%}, clean={result['clean']['accuracy']:.3%}, rejected={result['raw']['rejected']}", flush=True)
    np.savez_compressed(DIRECTORY / "scores.npz", **vectors)
    metadata["gates"] = gates(metadata["results"]["rgb"], metadata["results"]["current"])
    metadata["eligible"] = all(metadata["gates"].values())
    metadata["selected"] = "rgb" if metadata["eligible"] else "current"
    metadata["evidence_sha256"] = {p.name: digest(p) for p in (DIRECTORY / "scores.npz", DIRECTORY / "records.json", DIRECTORY / "source-split.npz")}
    metadata.update(status="DEVELOPMENT COMPLETE", completed_utc=datetime.now(timezone.utc).isoformat())
    verify(metadata)
    write_json(REPORT, metadata)
    write_json(DIRECTORY / "selection.json", {"selected": metadata["selected"], "report_sha256": digest(REPORT), "gates": metadata["gates"]})
    print("Selected:", metadata["selected"], metadata["gates"], flush=True)


def summary():
    output = ROOT / "reports" / (NAME + "-summary.md")
    if output.exists():
        raise FileExistsError("Preserve completed summary")
    d = json.loads(REPORT.read_text())
    verify(d)
    browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    if browser["status"] != "PASS":
        raise ValueError("Finish actual browser parity before summary")
    for name, value in d["evidence_sha256"].items():
        if digest(DIRECTORY / name) != value:
            raise ValueError("Evidence changed")
    lines = ["# Color-aware preprocessing: development results", "", "Fixed weights; single candidate; [frozen protocol](../docs/color-preprocessing.md).", "",
             "| Set | Current accuracy | RGB accuracy | Current correct >90% | RGB correct >90% | Current/RGB rejections |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for group in ("raw", "legacy", "color", "clean"):
        b,c = (d["results"][n][group] for n in ("current", "rgb"))
        lines.append(f"| {group} ({b['count']}) | {b['accuracy']:.3%} | {c['accuracy']:.3%} | {b['correct_above_90_fraction']:.3%} | {c['correct_above_90_fraction']:.3%} | {b['rejected']}/{c['rejected']} |")
    lines += ["", f"Development eligible: **{d['eligible']}**; selected: **{d['selected']}**.", "",
              "Gate results: " + ", ".join(k + "=" + ("PASS" if v else "FAIL") for k,v in d["gates"].items()) + ".", "",
              f"[Raw measurements and provenance]({NAME}.json). [Actual browser parity, uploads, activation and timing evidence]({NAME}-browser.json).", "",
              "Rejections count as incorrect; uniform vectors are only explicit NLL/Brier penalties. Strict >90% uses original unrounded model scores. "
              "Two palettes deliberately have almost identical grayscale brightness. Their frequency here does not estimate real CAPTCHA prevalence. "
              "The coding agent's visual spot-check is separate from independent human readability review, which is NOT RUN.", "",
              "Active app and all model weights remain unchanged. No training, reserved test, official CAPTCHA follow-up, deployment, CUDA setup, commit or push ran in this phase. "
              "Development eligibility is not official acceptance; the professor's all-ten confidence target remains unmet.", ""]
    output.write_text("\n".join(lines))
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    summary() if args.summary else run()
