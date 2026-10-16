"""Residual digit experiment with independent font-family development/test splits."""

import argparse
import copy
import hashlib
from io import BytesIO
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageFilter
import torch
from torch import nn
from torch.nn import functional as F

from .captcha import TRAIN_FONTS, render as render_simple
from .data import load_partition, split_indices
from .ensemble_benchmark import render as render_wavy
from .highres import EXTRA_FONTS, HighResCNN, render_broad
from .model import augment
from .preprocess import prepare, prepare_mnist
from .robust import evaluate
from .train import ROOT, write_json

NAME = "captcha-v3"
SEED = 20261123
ARCHITECTURE = "residual64-16-32-128"
ADDED_FONTS = ("DejaVuSerif.ttf", "LiberationMono-Regular.ttf", "pala.ttf", "gadugi.ttf", "malgun.ttf")
DEV_FONTS = ("CALIFR.TTF", "CENTAUR.TTF", "LeelawUI.ttf", "NotoSans-Regular.ttf")
TEST_FONTS = ("HTOWERT.TTF", "LTYPE.TTF", "sylfaen.ttf", "YuGothR.ttc")
POLICY = {"challenge_inputs_used": False, "seed": SEED, "development_count": 10000,
          "test_count": 20000, "minimum_raw_gain": .002, "clean_tolerance": .001,
          "desktop_p95_limit_ms": 150,
          "selection": "minimum raw development loss among epochs gaining at least 0.002 raw accuracy and losing at most 0.001 clean accuracy against captcha-v2",
          "scope": "Independent synthetic images, not collected real CAPTCHA population data",
          "development_fonts": DEV_FONTS, "test_fonts": TEST_FONTS}


class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        narrow = channels // 2
        self.reduce = nn.Conv2d(channels, narrow, 1)
        self.spatial = nn.Conv2d(narrow, narrow, 3, padding=1)
        self.expand = nn.Conv2d(narrow, channels, 1)
        nn.init.zeros_(self.expand.weight)
        nn.init.zeros_(self.expand.bias)

    def forward(self, x):
        return F.relu(x + self.expand(F.relu(self.spatial(F.relu(self.reduce(x))))))


class ResidualCNN(HighResCNN):
    """Baseline plus identity-initialized bottlenecks; no batchnorm in runtime."""
    def __init__(self):
        super().__init__()
        self.block1 = ResidualBlock(16)
        self.block2 = ResidualBlock(32)

    def features(self, x):
        first = self.block1(F.max_pool2d(F.relu(self.conv1(x)), 2))
        second = F.avg_pool2d(F.max_pool2d(F.relu(self.conv2(first)), 2), 2)
        second = self.block2(second)
        hidden = F.relu(self.fc1(second.flatten(1)))
        return first, second, hidden


def render(rng, digit, source, font):
    family = int(rng.integers(5))
    if family < 2:
        image = render_broad(rng, digit, source, font)
    elif family < 4:
        image = render_wavy(rng, digit, source, font, int(rng.integers(3)))
    else:
        image = render_simple(rng, digit, source=source, font_path=font)
    image = image.convert("RGB")
    if rng.random() < .3:
        image = image.filter(ImageFilter.GaussianBlur(float(rng.uniform(.15, .6))))
    if rng.random() < .3:
        values = np.asarray(image).astype(np.float32)
        values += rng.normal(0, rng.uniform(.6, 2), values.shape)
        image = Image.fromarray(np.clip(values, 0, 255).astype(np.uint8))
    if rng.random() < .3:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=int(rng.integers(55, 96)))
        buffer.seek(0)
        image = Image.open(buffer).convert("RGB")
    return image.convert("RGBA")


def make_raw(images, labels, indices, fonts, count, seed, fixtures=None):
    rng = np.random.default_rng(seed)
    x = np.empty((count, 1, 64, 64), np.float32)
    y = np.empty(count, np.int64)
    records = []
    for i in range(count):
        index = int(rng.choice(indices))
        printed = i % 2 == 0
        digit = (i // 2) % 10 if printed else int(labels[index])
        image = render(rng, digit, None if printed else images[index], fonts[int(rng.integers(len(fonts)))])
        x[i], y[i] = prepare(np.asarray(image), 64), digit
        if fixtures is not None and i < 60:
            fixtures.mkdir(parents=True, exist_ok=True)
            name = f"sample-{i:03d}.png"
            image.save(fixtures / name)
            records.append({"file": name, "expected": digit, "printed": printed})
    if fixtures is not None:
        write_json(fixtures / "labels.json", records)
    return torch.from_numpy(x), torch.from_numpy(y)


def run(args):
    directory = ROOT / "artifacts" / NAME
    report = ROOT / "reports" / f"{NAME}.json"
    if directory.exists() or report.exists():
        raise SystemExit("Preserve existing experiment")
    fonts = Path("C:/Windows/Fonts")
    train_fonts = [fonts / n for n in TRAIN_FONTS + EXTRA_FONTS + ADDED_FONTS]
    dev_fonts = [fonts / n for n in DEV_FONTS]
    for p in train_fonts + dev_fonts + [fonts / n for n in TEST_FONTS]:
        if not p.is_file():
            raise SystemExit(f"Missing font: {p}")
    directory.mkdir(parents=True)
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    baseline_path = ROOT / "artifacts/captcha-v2/best.pt"
    state = torch.load(baseline_path, map_location="cpu", weights_only=True)
    baseline = HighResCNN()
    baseline.load_state_dict(state)
    model = ResidualCNN()
    model.load_state_dict(state, strict=False)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    train, validation = split_indices(labels)
    clean = torch.from_numpy(prepare_mnist(images, 64))
    targets = torch.from_numpy(labels.astype(np.int64))
    vx, vy = clean[validation], targets[validation]
    print("Preparing fresh independent development images...", flush=True)
    rx, ry = make_raw(images, labels, validation, dev_fonts, POLICY["development_count"], SEED + 1)
    baseline_metrics = {"clean": evaluate(baseline, vx, vy), "raw": evaluate(baseline, rx, ry)}
    metadata = {"status": "TRAINING", "architecture": ARCHITECTURE, "policy": POLICY,
                "epochs_planned": args.epochs, "raw_train_per_epoch": args.samples,
                "baseline_checkpoint_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
                "baseline_validation": baseline_metrics, "history": [],
                "train_fonts": [p.name for p in train_fonts],
                "font_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in train_fonts + dev_fonts},
                "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "optimizer": {"name": "AdamW", "lr": .0003, "weight_decay": .0001, "batch_size": 128,
                              "scheduler": "cosine to 0.00002"}}
    write_json(report, metadata)
    print(f"Baseline development: clean {baseline_metrics['clean']['accuracy']:.2%}, raw {baseline_metrics['raw']['accuracy']:.2%}", flush=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.0003, weight_decay=.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.epochs, eta_min=.00002)
    best = float("inf")
    for epoch in range(args.epochs):
        start = time.perf_counter()
        tx, ty = make_raw(images, labels, train, train_fonts, args.samples, SEED + 100 + epoch)
        chosen = train[torch.randperm(len(train))[:args.samples // 2].numpy()]
        tx, ty = torch.cat((tx, clean[chosen])), torch.cat((ty, targets[chosen]))
        model.train()
        order = torch.randperm(len(tx))
        for begin in range(0, len(tx), 128):
            batch = order[begin:begin + 128]
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(model(augment(tx[batch])), ty[batch])
            loss.backward()
            optimizer.step()
        cm, rm = evaluate(model, vx, vy), evaluate(model, rx, ry)
        eligible = (cm["accuracy"] >= baseline_metrics["clean"]["accuracy"] - POLICY["clean_tolerance"]
                    and rm["accuracy"] >= baseline_metrics["raw"]["accuracy"] + POLICY["minimum_raw_gain"])
        if eligible and rm["loss"] < best:
            best = rm["loss"]
            torch.save(model.state_dict(), directory / "best.pt")
            metadata.update(selected_epoch=epoch + 1, validation={"clean": cm, "raw": rm})
        metadata["history"].append({"epoch": epoch + 1, "clean": cm, "raw": rm,
                                    "eligible": eligible, "seconds": time.perf_counter() - start})
        write_json(report, metadata)
        print(f"Epoch {epoch+1}/{args.epochs}: clean {cm['accuracy']:.2%}, raw {rm['accuracy']:.2%}, eligible={eligible}, {time.perf_counter()-start:.1f}s", flush=True)
        scheduler.step()
    torch.save(model.state_dict(), directory / "last.pt")
    metadata["status"] = "SELECTED: fresh test and browser QA NOT RUN" if (directory / "best.pt").exists() else "RETAIN BASELINE: no eligible epoch; fresh test NOT RUN"
    write_json(directory / "selection.json", {"selected_epoch": metadata.get("selected_epoch"),
               "policy": POLICY, "test_inputs_loaded": False})
    write_json(report, metadata)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--samples", type=int, default=40000)
    run(parser.parse_args())
