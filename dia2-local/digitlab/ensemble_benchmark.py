"""Independent synthetic development/test benchmark for frozen digit ensembles.

The official challenge and its generator are never read. Test scoring requires
a development selection and browser speed verification before it can begin.
"""

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from .platform_support import font_root, resolve_fonts
import platform

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version
import torch

from .data import load_partition, split_indices
from .highres import HighResCNN
from .model import DigitCNN
from .preprocess import prepare, prepare_mnist
from .train import ROOT, write_json

NAME = "ensemble-v1"
SEED = 20261111
DEV_FONTS = ("AGENCYR.TTF", "BOOKOS.TTF", "GOTHIC.TTF", "FRABK.TTF", "MAIAN.TTF", "DejaVuSans.ttf")
TEST_FONTS = ("BOD_R.TTF", "CENTURY.TTF", "GARA.TTF", "ROCK.TTF", "bahnschrift.ttf", "LiberationSans-Regular.ttf")
WEIGHTS = (0, .25, .5, .75, .9, 1)
POLICY = {
    "seed": SEED, "development_count": 10000, "test_count": 20000,
    "high_resolution_weights": WEIGHTS, "minimum_development_gain": .0015,
    "clean_development_tolerance": .001, "desktop_p95_limit_ms": 150,
    "selection": "maximum development raw accuracy subject to clean floor; ties use raw cross-entropy, then favor the 64px baseline",
    "challenge_inputs_used": False, "development_fonts": DEV_FONTS, "test_fonts": TEST_FONTS,
    "scope": "Fresh independent synthetic renderer, seeds and font families; MNIST source images are historical held-out images, not newly collected real CAPTCHA data",
}


def mix_scores(low, high, weight):
    low, high = np.asarray(low), np.asarray(high)
    if (low.shape != high.shape or low.ndim != 2 or low.shape[1] != 10
            or not 0 <= weight <= 1 or not np.isfinite(low).all() or not np.isfinite(high).all()
            or (low < 0).any() or (high < 0).any()):
        raise ValueError("Expected two finite nonnegative Nx10 score arrays and a weight in [0,1]")
    return low * (1 - weight) + high * weight


def metrics(scores, labels):
    prediction = scores.argmax(1)
    return {"count": len(labels), "correct": int((prediction == labels).sum()),
            "accuracy": float((prediction == labels).mean()),
            "loss": float(-np.log(np.maximum(scores[np.arange(len(labels)), labels], 1e-15)).mean())}


@lru_cache(maxsize=32)
def font(path):
    return ImageFont.truetype(path, 96)


def render(rng, digit, source, font_path, severity):
    """New renderer: nonsquare canvases, gradients, wavy curves and short cuts."""
    width, height = int(rng.integers(128, 177)), int(rng.integers(104, 145))
    base = rng.uniform(218, 254, (1, 1, 3))
    yy, xx = np.indices((height, width))
    gradient = (xx / width - .5) * rng.uniform(-24, 24) + (yy / height - .5) * rng.uniform(-18, 18)
    background = np.clip(base + gradient[:, :, None], 0, 255).astype(np.uint8)
    foreground = tuple(int(v) for v in rng.integers(5, 65, 3))
    inverted = rng.random() < .15
    if inverted:
        background = 255 - background
        foreground = tuple(255 - v for v in foreground)
    image = Image.fromarray(background)
    if source is None:
        glyph_font = font(str(font_path))
        box = glyph_font.getbbox(str(digit))
        mark = Image.new("L", (box[2] - box[0] + 4, box[3] - box[1] + 4))
        ImageDraw.Draw(mark).text((2 - box[0], 2 - box[1]), str(digit), font=glyph_font, fill=255)
    else:
        mark = Image.fromarray(source)
        mark = mark.crop(mark.getbbox())
    gh = int(height * rng.uniform(.48, .73))
    gw = max(7, min(int(width * .65), round(gh * mark.width / mark.height * rng.uniform(.8, 1.2))))
    mark = mark.resize((gw, gh), Image.Resampling.BICUBIC)
    # A single small cut; no whole strokes or glyphs are erased.
    if severity and rng.random() < .35:
        cx, cy = int(rng.integers(0, gw)), int(rng.integers(0, gh))
        ImageDraw.Draw(mark).line((cx, cy, min(gw - 1, cx + 5), cy), fill=0, width=1)
    mark = mark.rotate(float(rng.uniform(-17, 17)), Image.Resampling.BICUBIC, expand=True)
    x = (width - mark.width) // 2 + int(rng.integers(-7, 8))
    y = (height - mark.height) // 2 + int(rng.integers(-6, 7))
    image.paste(foreground, (x, y, x + mark.width, y + mark.height), mark)
    draw = ImageDraw.Draw(image)
    for _ in range(int(rng.integers(0, severity * 2 + 1))):
        blend = float(rng.uniform(.25, .85))
        bg = background[height // 2, width // 2]
        color = tuple(round(float(b) * (1 - blend) + f * blend) for b, f in zip(bg, foreground))
        phase = rng.uniform(0, 2 * np.pi)
        level = rng.uniform(0, height)
        slope = rng.uniform(-.35, .35)
        amplitude = rng.uniform(1, 9)
        points = [(px, round(level + slope * (px - width / 2) + amplitude * np.sin(px / 18 + phase)))
                  for px in range(0, width, 3)]
        draw.line(points, fill=color, width=int(rng.integers(1, 3)))
    for _ in range(int(rng.integers(0, severity * 15 + 1))):
        px, py = int(rng.integers(width)), int(rng.integers(height))
        radius = int(rng.integers(0, 3))
        draw.ellipse((px, py, px + radius, py + radius), fill=foreground)
    return image.convert("RGBA")


def load_models():
    low, high = DigitCNN(), HighResCNN()
    identities = {}
    for name, model in (("captcha-v1", low), ("captcha-v2", high)):
        directory = ROOT / "dist/model" / name / "digits"
        manifest = json.loads((directory / "manifest.json").read_text())
        assert hashlib.sha256((directory / "weights.bin").read_bytes()).hexdigest() == manifest["sha256"]
        model.load_state_dict(torch.load(ROOT / "artifacts" / name / "best.pt", map_location="cpu", weights_only=True))
        exported = b"".join(t.detach().numpy().astype("<f4").tobytes() for t in model.state_dict().values())
        assert hashlib.sha256(exported).hexdigest() == manifest["sha256"]
        model.eval()
        identities[name] = manifest["sha256"]
    return low, high, identities


@torch.no_grad()
def scores(model, x):
    logits = model(torch.from_numpy(x)).double()
    return logits.softmax(1).numpy()


def collect(models, images, labels, indices, fonts, count, seed, directory):
    rng = np.random.default_rng(seed)
    low_scores, high_scores, targets, kinds, severities = [], [], [], [], []
    fixtures = []
    for start in range(0, count, 128):
        low, high, batch_y = [], [], []
        for i in range(start, min(start + 128, count)):
            printed = i % 2 == 0
            index = int(rng.choice(indices))
            digit = (i // 2) % 10 if printed else int(labels[index])
            severity = i % 3
            image = render(rng, digit, None if printed else images[index], fonts[int(rng.integers(len(fonts)))], severity)
            rgba = np.asarray(image)
            low.append(prepare(rgba)); high.append(prepare(rgba, 64)); batch_y.append(digit)
            kinds.append(int(printed)); severities.append(severity)
            if i < 60:
                directory.mkdir(parents=True, exist_ok=True)
                name = f"sample-{i:05d}.png"
                image.save(directory / name)
                fixtures.append({"file": name, "expected": digit, "printed": printed, "severity": severity})
        low_scores.append(scores(models[0], np.stack(low)))
        high_scores.append(scores(models[1], np.stack(high)))
        targets.extend(batch_y)
        if start % 2560 == 0:
            print(f"Rendered and classified {min(start + 128, count)}/{count}", flush=True)
    write_json(directory / "labels.json", fixtures)
    return {"low": np.concatenate(low_scores), "high": np.concatenate(high_scores),
            "labels": np.array(targets), "printed": np.array(kinds), "severity": np.array(severities)}


def summarize(data, weight):
    combined = mix_scores(data["low"], data["high"], weight)
    labels = data["labels"]
    a, b, c = data["low"].argmax(1), data["high"].argmax(1), combined.argmax(1)
    return {"high_resolution_weight": weight, "overall": metrics(combined, labels),
            "by_source": {name: metrics(combined[data["printed"] == value], labels[data["printed"] == value])
                          for name, value in (("printed", 1), ("handwritten", 0))},
            "by_severity": {str(value): metrics(combined[data["severity"] == value], labels[data["severity"] == value]) for value in range(3)},
            "complementarity": {"both_correct": int(((a == labels) & (b == labels)).sum()),
                "only_28_correct": int(((a == labels) & (b != labels)).sum()),
                "only_64_correct": int(((a != labels) & (b == labels)).sum()),
                "both_wrong": int(((a != labels) & (b != labels)).sum()),
                "ensemble_fixes_baseline": int(((c == labels) & (b != labels)).sum()),
                "ensemble_breaks_baseline": int(((c != labels) & (b == labels)).sum())}}


def run(args):
    torch.set_num_threads(4)
    directory = ROOT / "artifacts" / NAME
    report_path = ROOT / "reports" / f"{NAME}-{args.stage}.json"
    if report_path.exists() or (directory / f"{args.stage}.npz").exists():
        raise SystemExit("Stage already exists; preserve its evidence")
    fonts = resolve_fonts(args.fonts, DEV_FONTS if args.stage == "development" else TEST_FONTS)
    for path in fonts:
        if not path.is_file():
            raise SystemExit(f"Missing required font: {path}")
    low, high, identities = load_models()
    directory.mkdir(parents=True, exist_ok=True)
    if args.stage == "test":
        selection = json.loads((directory / "selection.json").read_text())
        speed = json.loads((ROOT / "reports/ensemble-v1-speed-qa.json").read_text())
        assert speed["status"] == "PASS" and speed["model_identities"] == identities
        assert speed["p95_ms"] < POLICY["desktop_p95_limit_ms"]
        assert selection["model_identities"] == identities
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", args.stage == "development")
    indices = split_indices(labels)[1] if args.stage == "development" else np.arange(len(labels))
    data = collect((low, high), images, labels, indices, fonts,
                   POLICY["development_count"] if args.stage == "development" else POLICY["test_count"],
                   SEED if args.stage == "development" else SEED + 1, directory / args.stage / "fixtures")
    np.savez_compressed(directory / f"{args.stage}.npz", **data)
    clean_images, clean_y = images[indices], labels[indices]
    clean_low, clean_high = [], []
    for start in range(0, len(clean_y), 128):
        batch = clean_images[start:start + 128]
        clean_low.append(scores(low, prepare_mnist(batch)))
        clean_high.append(scores(high, prepare_mnist(batch, 64)))
    clean_low, clean_high = np.concatenate(clean_low), np.concatenate(clean_high)
    baseline_clean = metrics(clean_high, clean_y)
    if args.stage == "development":
        candidates = []
        for weight in WEIGHTS:
            candidate = summarize(data, weight)
            candidate["clean"] = metrics(mix_scores(clean_low, clean_high, weight), clean_y)
            candidate["eligible"] = candidate["clean"]["accuracy"] >= baseline_clean["accuracy"] - POLICY["clean_development_tolerance"]
            candidates.append(candidate)
        eligible = [c for c in candidates if c["eligible"]]
        winner = min(eligible, key=lambda c: (-c["overall"]["correct"], c["overall"]["loss"], -c["high_resolution_weight"]))
        baseline_raw = metrics(data["high"], data["labels"])
        improvement = winner["overall"]["accuracy"] - baseline_raw["accuracy"]
        selected_weight = winner["high_resolution_weight"] if improvement >= POLICY["minimum_development_gain"] else 1
        selection = {"model_identities": identities, "high_resolution_weight": selected_weight,
                     "development_gain": improvement, "ensemble_selected": selected_weight not in (0, 1),
                     "policy": POLICY, "test_inputs_loaded": False}
        write_json(directory / "selection.json", selection)
        details = {"candidates": candidates, "selection": selection}
    else:
        weight = selection["high_resolution_weight"]
        details = {"selected": summarize(data, weight), "baseline": summarize(data, 1),
                   "previous_28px": summarize(data, 0),
                   "clean_selected": metrics(mix_scores(clean_low, clean_high, weight), clean_y),
                   "clean_baseline": baseline_clean, "selection": selection}
    report = {"status": "PASS", "stage": args.stage, "policy": POLICY, "model_identities": identities,
              "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "font_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in fonts},
              "cache_sha256": hashlib.sha256((directory / f"{args.stage}.npz").read_bytes()).hexdigest(),
              "environment": {"python": platform.python_version(), "torch": torch.__version__,
                              "numpy": np.__version__, "pillow": pillow_version}, **details}
    write_json(report_path, report)
    print(json.dumps(details.get("selection", details.get("selected")), indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("development", "test"), required=True)
    parser.add_argument("--fonts", type=Path, default=font_root())
    run(parser.parse_args())


if __name__ == "__main__":
    main()
