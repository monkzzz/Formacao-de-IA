"""64px CAPTCHA-style experiment; no challenge inputs or generator are read."""

import argparse
from functools import lru_cache
import hashlib
from pathlib import Path

from .platform_support import font_root, resolve_fonts
import platform
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, __version__ as pillow_version
import torch
from torch import nn
from torch.nn import functional as F

from .captcha import TRAIN_FONTS, HELDOUT_FONTS, render
from .data import load_partition, split_indices
from .model import DigitCNN, augment
from .preprocess import VERSION64, prepare, prepare_mnist
from .robust import evaluate
from .train import ROOT, write_json

SEED = 20261030
ARCHITECTURE = "cnn64-16-32-128"
EXTRA_FONTS = ("arialbi.ttf", "timesbi.ttf", "couri.ttf", "calibrii.ttf",
               "verdanai.ttf", "georgiab.ttf", "georgiai.ttf", "trebucbd.ttf",
               "comicbd.ttf", "consolab.ttf", "segoeuib.ttf", "tahomabd.ttf",
               "ARIALN.TTF", "ARIALNB.TTF")


class HighResCNN(nn.Module):
    """64px -> conv16/maxpool32 -> conv32/maxpool16/avgpool8 -> dense128."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, 10)
        self.dropout = nn.Dropout(.25)

    def features(self, x):
        first = F.max_pool2d(F.relu(self.conv1(x)), 2)
        second = F.avg_pool2d(F.max_pool2d(F.relu(self.conv2(first)), 2), 2)
        hidden = F.relu(self.fc1(second.flatten(1)))
        return first, second, hidden

    def forward(self, x):
        return self.fc2(self.dropout(self.features(x)[2]))

    def initialize_from(self, state):
        copied = {name: value.clone() for name, value in state.items()}
        copied["fc1.weight"] = F.interpolate(state["fc1.weight"].reshape(128, 32, 7, 7),
            (8, 8), mode="bilinear", align_corners=False).reshape(128, -1) * (49 / 64)
        self.load_state_dict(copied)


def render_broad(rng, digit, source, font_path):
    """Independent broadening: larger canvas, shear, short gaps and curves."""
    # Reuse the previous independent renderer, never the official generator.
    image = render(rng, digit, source=source, font_path=font_path)
    # Work at a larger native resolution for printed glyphs to preserve detail.
    if source is None:
        font = get_font(str(font_path))
        mark = Image.new("L", (112, 112))
        box = font.getbbox(str(digit))
        ImageDraw.Draw(mark).text(((112 - box[2] + box[0]) / 2 - box[0],
                                  (112 - box[3] + box[1]) / 2 - box[1]), str(digit), font=font, fill=255)
        mark = mark.crop(mark.getbbox())
    else:
        mark = Image.fromarray(source).crop(Image.fromarray(source).getbbox())
    height = int(rng.integers(47, 81))
    width = max(8, min(80, round(mark.width / mark.height * height * rng.uniform(.75, 1.25))))
    mark = mark.resize((width, height), Image.Resampling.BILINEAR)
    if rng.random() < .25:
        mark = mark.filter(ImageFilter.MaxFilter(3))
    # Short cuts can break a stroke, but never erase a whole glyph.
    if rng.random() < .40:
        draw = ImageDraw.Draw(mark)
        x, y = int(rng.integers(0, width)), int(rng.integers(0, height))
        draw.line((x, y, min(width - 1, x + int(rng.integers(3, 9))), y), fill=0, width=1)
    mark = mark.rotate(float(rng.uniform(-22, 22)), Image.Resampling.BICUBIC, expand=True)
    shear = float(rng.uniform(-.18, .18))
    mark = mark.transform(mark.size, Image.Transform.AFFINE,
        (1, shear, -shear * mark.height / 2, 0, 1, 0), Image.Resampling.BILINEAR)
    # Recover independently drawn colors; no special casing by label or filename.
    background = tuple(int(v) for v in rng.integers(210, 256, 3))
    foreground = tuple(int(v) for v in rng.integers(0, 65, 3))
    if rng.random() < .15:
        background, foreground = foreground, background
    canvas = Image.new("RGB", (112, 112), background)
    x = max(0, (112 - mark.width) // 2 + int(rng.integers(-8, 9)))
    y = max(0, (112 - mark.height) // 2 + int(rng.integers(-8, 9)))
    canvas.paste(foreground, (x, y, x + mark.width, y + mark.height), mark)
    draw = ImageDraw.Draw(canvas)
    severity = int(rng.choice([0, 1, 2], p=[.15, .40, .45]))
    for _ in range(int(rng.integers(0, 3 * severity + 1))):
        blend = float(rng.uniform(.3, 1))
        color = tuple(round(b * (1 - blend) + f * blend) for b, f in zip(background, foreground))
        points = [int(v) for v in rng.integers(0, 112, 4)]
        if rng.random() < .5:
            draw.line(points, fill=color, width=int(rng.integers(1, 4)))
        else:
            left, right = sorted(points[::2])
            top, bottom = sorted(points[1::2])
            draw.arc((left, top, right, bottom), int(rng.integers(0, 90)),
                     int(rng.integers(180, 360)), fill=color, width=int(rng.integers(1, 3)))
    for _ in range(int(rng.integers(0, 20 * severity + 1))):
        px, py = (int(v) for v in rng.integers(0, 112, 2))
        radius = int(rng.integers(0, 3))
        draw.ellipse((px, py, px + radius, py + radius), fill=foreground)
    # Include the old independent noise family as well as the broader one.
    return image if rng.random() < .30 else canvas.convert("RGBA")


@lru_cache(maxsize=64)
def get_font(path):
    return ImageFont.truetype(path, 84)


def make_raw(images, labels, indices, fonts, count, seed, fixture_dir=None):
    rng = np.random.default_rng(seed)
    high = np.empty((count, 1, 64, 64), np.float32)
    low = np.empty((count, 1, 28, 28), np.float32)
    targets = np.empty(count, np.int64)
    fixtures = []
    for i in range(count):
        index = int(rng.choice(indices))
        printed = i % 2 == 0
        digit = (i // 2) % 10 if printed else int(labels[index])
        image = render_broad(rng, digit, None if printed else images[index], fonts[int(rng.integers(len(fonts)))])
        rgba = np.asarray(image)
        high[i], low[i], targets[i] = prepare(rgba, 64), prepare(rgba), digit
        if fixture_dir is not None and i < 60:
            fixture_dir.mkdir(parents=True, exist_ok=True)
            name = f"sample-{i:03d}.png"
            image.save(fixture_dir / name)
            fixtures.append({"file": name, "expected": digit, "printed": printed})
    if fixture_dir is not None:
        write_json(fixture_dir / "labels.json", fixtures)
    return torch.from_numpy(high), torch.from_numpy(low), torch.from_numpy(targets)


def export(model, directory, metadata, inputs):
    directory.mkdir(parents=True)
    chunks, tensors, offset = [], [], 0
    for name, tensor in model.state_dict().items():
        values = tensor.detach().numpy().astype("<f4")
        chunks.append(values.tobytes())
        tensors.append({"name": name, "shape": list(values.shape), "offset": offset, "length": values.size})
        offset += values.size
    blob = b"".join(chunks)
    (directory / "weights.bin").write_bytes(blob)
    manifest = {"schema": 1, "architecture": ARCHITECTURE, "task": "digits", "labels": list("0123456789"),
                "input_side": 64, "feature_sides": [32, 8], "preprocessing": VERSION64,
                "dtype": "float32-le", "sha256": hashlib.sha256(blob).hexdigest(),
                "bytes": len(blob), "tensors": tensors, "training": metadata}
    write_json(directory / "manifest.json", manifest)
    model.eval()
    with torch.no_grad():
        logits = model(inputs)
        first, second, hidden = model.features(inputs)
    write_json(directory / "parity.json", {"model_sha256": manifest["sha256"], "absolute_tolerance": .0001,
        "cases": [{"label": str(i), "input": inputs[i].flatten().tolist(), "logits": logits[i].tolist(),
                   "pool1": first[i].flatten().tolist(), "pool2": second[i].flatten().tolist(),
                   "hidden": hidden[i].tolist()} for i in range(len(inputs))]})
    return manifest


def run(args):
    directory = ROOT / "artifacts" / args.name
    report_path = ROOT / "reports" / f"{args.name}.json"
    destination = ROOT / "dist/model" / args.name / "digits"
    if directory.exists() or report_path.exists() or destination.exists():
        raise SystemExit("Preserve existing experiments; choose a new --name")
    train_fonts = resolve_fonts(args.fonts, TRAIN_FONTS + EXTRA_FONTS)
    heldout_fonts = resolve_fonts(args.fonts, HELDOUT_FONTS)
    for path in train_fonts + heldout_fonts:
        if not path.is_file():
            raise SystemExit(f"Missing font: {path}")
    directory.mkdir(parents=True)
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    baseline_path = ROOT / "artifacts/captcha-v1/best.pt"
    state = torch.load(baseline_path, map_location="cpu", weights_only=True)
    baseline = DigitCNN()
    baseline.load_state_dict(state)
    model = HighResCNN()
    model.initialize_from(state)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    train, validation = split_indices(labels)
    np.savez(directory / "split.npz", train=train, validation=validation)
    print("Preparing 64px clean and independent noisy validation inputs...", flush=True)
    clean = torch.from_numpy(prepare_mnist(images, 64))
    targets = torch.from_numpy(labels.astype(np.int64))
    vx, vy = clean[validation], targets[validation]
    rvx, low_vx, rvy = make_raw(images, labels, validation, heldout_fonts, 5000, SEED + 1)
    low_clean = torch.from_numpy(prepare_mnist(images[validation]))
    baseline_metrics = {"clean": evaluate(baseline, low_clean, vy), "raw": evaluate(baseline, low_vx, rvy)}
    metadata = {"task": "digits", "preprocessing": VERSION64, "epochs_planned": args.epochs,
        "seed": SEED, "threads": args.threads, "split": {"train": len(train), "validation": len(validation)},
        "raw_train_per_epoch": args.samples, "baseline_checkpoint_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        "baseline_validation": baseline_metrics, "policy": {
            "challenge_inputs_used": False, "validation_seed": SEED + 1, "test_seed": SEED + 2,
            "selection": "minimum raw validation loss subject to clean accuracy within 0.003 of baseline and raw accuracy above baseline",
            "clean_accuracy_tolerance": .003, "train_fonts": [p.name for p in train_fonts],
            "heldout_font_families": HELDOUT_FONTS, "raw_corruption": "30% previous independent renderer, 70% 112px native glyphs, shear/rotation, short stroke gaps, up to six lines/arcs and 40 speckles"},
        "environment": {"python": platform.python_version(), "torch": torch.__version__,
                        "numpy": np.__version__, "pillow": pillow_version, "device": "cpu"},
        "optimizer": {"name": "AdamW", "lr": .0003, "weight_decay": .0001, "batch_size": 128,
                      "scheduler": "cosine to 0.00002"},
        "font_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in train_fonts + heldout_fonts},
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "history": [], "status": "TRAINING"}
    write_json(report_path, metadata)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.0003, weight_decay=.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.epochs, eta_min=.00002)
    checkpoint = directory / "best.pt"
    best = float("inf")
    for epoch in range(args.epochs):
        start = time.perf_counter()
        rx, _, ry = make_raw(images, labels, train, train_fonts, args.samples, SEED + 100 + epoch)
        chosen = train[torch.randperm(len(train))[:args.samples // 2].numpy()]
        tx, ty = torch.cat((rx, clean[chosen])), torch.cat((ry, targets[chosen]))
        model.train()
        order = torch.randperm(len(tx))
        for begin in range(0, len(tx), 128):
            indices = order[begin:begin + 128]
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(model(augment(tx[indices])), ty[indices])
            loss.backward()
            optimizer.step()
        cm, rm = evaluate(model, vx, vy), evaluate(model, rvx, rvy)
        eligible = (cm["accuracy"] >= baseline_metrics["clean"]["accuracy"] - .003
                    and rm["accuracy"] > baseline_metrics["raw"]["accuracy"])
        if eligible and rm["loss"] < best:
            best = rm["loss"]
            torch.save(model.state_dict(), checkpoint)
            metadata["selected_epoch"] = epoch + 1
            metadata["validation"] = {"clean": cm, "raw": rm}
        metadata["history"].append({"epoch": epoch + 1, "clean": cm, "raw": rm,
                                    "eligible": eligible, "seconds": time.perf_counter() - start})
        write_json(report_path, metadata)
        print(f"Epoch {epoch+1}/{args.epochs}: clean {cm['accuracy']:.2%}, noisy {rm['accuracy']:.2%}, eligible={eligible}, {time.perf_counter()-start:.1f}s", flush=True)
        scheduler.step()
    if not checkpoint.exists():
        metadata["status"] = "FAIL: no eligible candidate; active model retained"
        write_json(report_path, metadata)
        return
    # Selection is frozen before loading official test images.
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    test_images, test_labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    test_x = torch.from_numpy(prepare_mnist(test_images, 64))
    test_y = torch.from_numpy(test_labels.astype(np.int64))
    raw_tx, low_tx, raw_ty = make_raw(test_images, test_labels, np.arange(len(test_y)), heldout_fonts,
                                    10000, SEED + 2, directory / "fixtures")
    metadata["test"] = evaluate(model, test_x, test_y)
    metadata["raw_test"] = evaluate(model, raw_tx, raw_ty)
    metadata["baseline_test"] = {"clean": evaluate(baseline, torch.from_numpy(prepare_mnist(test_images)), test_y),
                                 "raw": evaluate(baseline, low_tx, raw_ty)}
    metadata["status"] = "PASS: selected on validation only; challenge NOT RUN at export"
    indices = [int(torch.nonzero(test_y == digit)[0]) for digit in range(10)]
    manifest = export(model, destination, metadata, test_x[indices])
    metadata["model_sha256"] = manifest["sha256"]
    write_json(report_path, metadata)
    print(f"Frozen 64px model: clean {metadata['test']['accuracy']:.2%}, raw {metadata['raw_test']['accuracy']:.2%}; baseline raw {metadata['baseline_test']['raw']['accuracy']:.2%}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="captcha-v2")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--samples", type=int, default=40000)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--fonts", type=Path, default=font_root())
    args = parser.parse_args()
    if not args.name.replace("-", "").isalnum() or min(args.epochs, args.samples, args.threads) < 1:
        parser.error("Use a simple experiment name and positive counts")
    run(args)


if __name__ == "__main__":
    main()
