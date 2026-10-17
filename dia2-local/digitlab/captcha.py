"""Independent raw-image CAPTCHA-style training; never reads challenge inputs.

Noise is rendered BEFORE the exact browser preprocessing, so peripheral marks
affect cropping and centering during learning as they do during real uploads.
"""

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from .platform_support import font_root, resolve_fonts
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import torch
from torch.nn import functional as F

from .data import load_partition, split_indices
from .model import DigitCNN, augment
from .preprocess import VERSION, prepare, prepare_mnist
from .robust import evaluate, export
from .train import ROOT, write_json

SEED = 20261021
TRAIN_FONTS = (
    "arial.ttf", "arialbd.ttf", "ariali.ttf", "times.ttf", "timesbd.ttf",
    "cour.ttf", "courbd.ttf", "calibri.ttf", "calibrib.ttf", "verdana.ttf",
    "verdanab.ttf", "tahoma.ttf", "georgia.ttf", "trebuc.ttf", "comic.ttf",
    "consola.ttf", "segoeui.ttf",
)
HELDOUT_FONTS = ("cambria.ttc", "Candara.ttf", "constan.ttf", "corbel.ttf")
POLICY = {
    "seed": SEED, "validation_seed": SEED + 1, "test_seed": SEED + 2,
    "challenge_inputs_used": False,
    "selection": "lowest raw-image validation cross-entropy with clean MNIST validation accuracy within 0.003 of baseline and raw-image accuracy above baseline",
    "clean_accuracy_tolerance": .003,
    "train_fonts": TRAIN_FONTS, "heldout_font_families": HELDOUT_FONTS,
    "raw_corruption": "64px colored backgrounds, polarity, rotation +/-18 degrees, aspect/scale/position variation, 0-4 lines/arcs and 0-24 speckles; then unchanged browser preprocessing",
    "evaluation": "Separate MNIST source indices and held-out font families; fixed validation/test seeds; no claim of real CAPTCHA population accuracy",
}


@lru_cache(maxsize=256)
def glyph(font_path, digit):
    font = ImageFont.truetype(str(font_path), 48)
    box = font.getbbox(str(digit))
    image = Image.new("L", (box[2] - box[0] + 4, box[3] - box[1] + 4))
    ImageDraw.Draw(image).text((2 - box[0], 2 - box[1]), str(digit), font=font, fill=255)
    return image


def render(rng, digit, source=None, font_path=None):
    """Render a single labeled glyph without any challenge-derived parameters."""
    if source is None:
        mark = glyph(str(font_path), int(digit)).copy()
    else:
        mark = Image.fromarray(source)
        mark = mark.crop(mark.getbbox())
    height = int(rng.integers(29, 49))
    width = max(5, min(48, round(mark.width / mark.height * height * rng.uniform(.8, 1.2))))
    mark = mark.resize((width, height), Image.Resampling.BILINEAR)
    if rng.random() < .25:
        mark = mark.filter(ImageFilter.MaxFilter(3))
    mark = mark.rotate(float(rng.uniform(-18, 18)), Image.Resampling.BICUBIC, expand=True)
    background = tuple(int(v) for v in rng.integers(205, 256, 3))
    foreground = tuple(int(v) for v in rng.integers(0, 65, 3))
    if rng.random() < .15:
        background, foreground = foreground, background
    image = Image.new("RGB", (64, 64), background)
    x = max(0, (64 - mark.width) // 2 + int(rng.integers(-5, 6)))
    y = max(0, (64 - mark.height) // 2 + int(rng.integers(-5, 6)))
    image.paste(foreground, (x, y, x + mark.width, y + mark.height), mark)
    draw = ImageDraw.Draw(image)
    severity = rng.choice([0, 1, 2], p=[.20, .40, .40])
    for _ in range(int(rng.integers(0, 2 * severity + 1))):
        blend = float(rng.uniform(.25, .9))
        color = tuple(round(b * (1 - blend) + f * blend) for b, f in zip(background, foreground))
        points = [int(v) for v in rng.integers(0, 64, 4)]
        if rng.random() < .5:
            draw.line(points, fill=color, width=int(rng.integers(1, 3)))
        else:
            left, right = sorted(points[::2])
            top, bottom = sorted(points[1::2])
            draw.arc((left, top, right, bottom), 0, int(rng.integers(90, 350)), fill=color, width=1)
    for _ in range(int(rng.integers(0, 12 * severity + 1))):
        px, py = (int(v) for v in rng.integers(0, 64, 2))
        radius = int(rng.integers(0, 2))
        draw.ellipse((px, py, px + radius, py + radius), fill=foreground)
    return image.convert("RGBA")


def make_raw(images, labels, indices, fonts, count, seed, fixture_dir=None):
    rng = np.random.default_rng(seed)
    x = np.empty((count, 1, 28, 28), np.float32)
    y = np.empty(count, np.int64)
    fixtures = []
    for i in range(count):
        printed = i % 2 == 0
        index = int(rng.choice(indices))
        digit = (i // 2) % 10 if printed else int(labels[index])
        image = render(rng, digit, source=None if printed else images[index],
                       font_path=fonts[int(rng.integers(len(fonts)))])
        x[i] = prepare(np.asarray(image))
        y[i] = digit
        if fixture_dir is not None and i < 40:
            fixture_dir.mkdir(parents=True, exist_ok=True)
            name = f"sample-{i:03d}.png"
            image.save(fixture_dir / name)
            fixtures.append({"file": name, "expected": digit, "printed": printed})
    if fixtures:
        write_json(fixture_dir / "labels.json", fixtures)
    return torch.from_numpy(x), torch.from_numpy(y)


def run(args):
    directory = ROOT / "artifacts" / args.name
    report_path = ROOT / "reports" / f"{args.name}.json"
    destination = ROOT / "dist/model" / args.name / "digits"
    if directory.exists() or report_path.exists() or destination.exists():
        raise SystemExit("Experiment already exists; choose a new --name. Existing evidence is preserved.")
    train_fonts = resolve_fonts(args.fonts, TRAIN_FONTS)
    heldout_fonts = resolve_fonts(args.fonts, HELDOUT_FONTS)
    for path in train_fonts + heldout_fonts:
        if not path.is_file():
            raise SystemExit(f"Required font missing: {path}")
    directory.mkdir(parents=True)
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    baseline_path = ROOT / "artifacts/robust/digits/best.pt"
    baseline_state = torch.load(baseline_path, map_location="cpu", weights_only=True)
    model = DigitCNN()
    model.load_state_dict(baseline_state)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    train, validation = split_indices(labels)
    np.savez(directory / "split.npz", train=train, validation=validation)
    print("Preparing clean inputs and independent raw-image validation...", flush=True)
    clean = torch.from_numpy(prepare_mnist(images))
    targets = torch.from_numpy(labels.astype(np.int64))
    vx, vy = clean[validation], targets[validation]
    raw_vx, raw_vy = make_raw(images, labels, validation, heldout_fonts, 5000, SEED + 1)
    baseline = {"clean": evaluate(model, vx, vy), "raw": evaluate(model, raw_vx, raw_vy)}
    metadata = {"task": "digits", "preprocessing": VERSION, "policy": POLICY,
                "epochs_planned": args.epochs, "threads": args.threads,
                "split": {"train": len(train), "validation": len(validation)},
                "raw_train_per_epoch": args.samples, "raw_validation": len(raw_vy),
                "baseline_checkpoint_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
                "font_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in train_fonts + heldout_fonts},
                "baseline_validation": baseline, "history": [], "status": "TRAINING"}
    write_json(report_path, metadata)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.0003, weight_decay=.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.epochs, eta_min=.00002)
    checkpoint = directory / "best.pt"
    best = float("inf")
    for epoch in range(args.epochs):
        start = time.perf_counter()
        # Fresh rendering each epoch, from training indices/families only.
        rx, ry = make_raw(images, labels, train, train_fonts, args.samples, SEED + 100 + epoch)
        chosen = train[torch.randperm(len(train))[:args.samples // 2].numpy()]
        tx, ty = torch.cat((rx, clean[chosen])), torch.cat((ry, targets[chosen]))
        order = torch.randperm(len(tx))
        model.train()
        for begin in range(0, len(tx), 256):
            indices = order[begin:begin + 256]
            batch = tx[indices]
            # Only mild pixel augmentation; raw rendering already adds clutter.
            batch = augment(batch)
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(model(batch), ty[indices])
            loss.backward()
            optimizer.step()
        clean_metrics, raw_metrics = evaluate(model, vx, vy), evaluate(model, raw_vx, raw_vy)
        eligible = (clean_metrics["accuracy"] >= baseline["clean"]["accuracy"] - .003
                    and raw_metrics["accuracy"] > baseline["raw"]["accuracy"])
        if eligible and raw_metrics["loss"] < best:
            best = raw_metrics["loss"]
            torch.save(model.state_dict(), checkpoint)
            metadata["selected_epoch"] = epoch + 1
            metadata["validation"] = {"clean": clean_metrics, "raw": raw_metrics}
        metadata["history"].append({"epoch": epoch + 1, "clean": clean_metrics, "raw": raw_metrics,
                                    "eligible": eligible, "seconds": time.perf_counter() - start})
        write_json(report_path, metadata)
        print(f"Epoch {epoch+1}/{args.epochs}: clean {clean_metrics['accuracy']:.2%}, raw {raw_metrics['accuracy']:.2%}, eligible={eligible}, {time.perf_counter()-start:.1f}s", flush=True)
        scheduler.step()
    if not checkpoint.exists():
        metadata["status"] = "FAIL: no eligible candidate; active model retained"
        write_json(report_path, metadata)
        return
    # Model selection ends here. Test data is loaded once, afterwards.
    model.load_state_dict(torch.load(checkpoint, weights_only=True, map_location="cpu"))
    test_images, test_labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    test_x = torch.from_numpy(prepare_mnist(test_images))
    test_y = torch.from_numpy(test_labels.astype(np.int64))
    raw_tx, raw_ty = make_raw(test_images, test_labels, np.arange(len(test_y)), heldout_fonts,
                             10000, SEED + 2, directory / "fixtures")
    baseline_model = DigitCNN()
    baseline_model.load_state_dict(baseline_state)
    metadata["baseline_test"] = {"clean": evaluate(baseline_model, test_x, test_y),
                                 "raw": evaluate(baseline_model, raw_tx, raw_ty)}
    metadata["test"] = evaluate(model, test_x, test_y)
    metadata["raw_test"] = evaluate(model, raw_tx, raw_ty)
    metadata["status"] = "PASS: selected on independent validation; challenge NOT RUN"
    indices = [int(torch.nonzero(test_y == digit)[0]) for digit in range(10)]
    manifest = export(model, destination, metadata, test_x[indices], list("0123456789"))
    metadata["model_sha256"] = manifest["sha256"]
    write_json(report_path, metadata)
    print(f"Frozen selected model: clean test {metadata['test']['accuracy']:.2%}; raw synthetic test {metadata['raw_test']['accuracy']:.2%}; baseline raw {metadata['baseline_test']['raw']['accuracy']:.2%}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="captcha-v1")
    parser.add_argument("--fonts", type=Path, default=font_root())
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--samples", type=int, default=40000)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if not args.name.replace("-", "").isalnum() or min(args.epochs, args.samples, args.threads) < 1:
        parser.error("Use an alphanumeric/hyphen experiment name and positive counts")
    run(args)


if __name__ == "__main__":
    main()
