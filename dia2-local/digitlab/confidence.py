"""Independent residual fine-tuning with proper-score and confidence diagnostics.

The official challenge, its generator, answers and recorded predictions are never
loaded here. No temperature adjustment or display-score rescaling is performed.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
from PIL import __version__ as pillow_version
import torch
from torch.nn import functional as F

from .captcha import TRAIN_FONTS
from .data import load_partition, split_indices
from .highres import EXTRA_FONTS
from .model import augment
from .preprocess import prepare_mnist
from .residual import ADDED_FONTS, ARCHITECTURE, ResidualCNN, make_raw
from .train import ROOT, write_json

NAME = "captcha-confidence-v1"
SEED = 2026101701
DEV_FONTS = ("CALIFR.TTF", "CENTAUR.TTF", "LeelawUI.ttf", "NotoSans-Regular.ttf", "BOOKOS.TTF", "GOTHIC.TTF")
TEST_FONTS = ("BELL.TTF", "BRLNSR.TTF", "PER_____.TTF", "TCM_____.TTF")
POLICY = {
    "seed": SEED, "epochs": 8, "raw_per_epoch": 30000, "clean_per_epoch": 15000,
    "development_count": 6000, "test_count": 10000, "batch_size": 128,
    "optimizer": "AdamW lr=0.0001, weight_decay=0.0001; cosine to 0.000005",
    "objective": "Unmodified cross entropy on independent raw synthetic and clean training images",
    "selection": "Minimum raw development NLL among eligible epochs; no official inputs",
    "gates": {"raw_accuracy_tolerance": .001, "clean_accuracy_tolerance": .001,
              "minimum_correct_90_coverage_gain": .005, "brier_tolerance": .001,
              "ece_tolerance": .005, "nll_must_improve": True},
    "challenge_used_for_training_selection_or_calibration": False,
    "temperature": 1.0, "preprocessing_change": False,
    "prior_exposure": "Baseline has historical MNIST/synthetic/challenge evaluations; new seeds and test font families, not a new blind real-world study",
}


def score_metrics(scores, labels):
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    if scores.shape != (len(labels), 10) or not len(labels):
        raise ValueError("Expected nonempty Nx10 scores")
    if not np.isfinite(scores).all() or (scores < 0).any() or not np.allclose(scores.sum(1), 1, atol=1e-5):
        raise ValueError("Scores must be finite probabilities summing to one")
    prediction = scores.argmax(1)
    confidence = scores.max(1)
    correct = prediction == labels
    high = confidence >= .9
    ece = 0.0
    for lower in np.arange(0, 1, .1):
        mask = (confidence > lower) & (confidence <= min(1, lower + .1))
        if mask.any():
            ece += mask.mean() * abs(correct[mask].mean() - confidence[mask].mean())
    target = np.eye(10)[labels]
    confusion = np.zeros((10, 10), dtype=int)
    np.add.at(confusion, (labels, prediction), 1)
    return {"count": len(labels), "correct": int(correct.sum()), "accuracy": float(correct.mean()),
            "loss": float(-np.log(np.maximum(scores[np.arange(len(labels)), labels], 1e-15)).mean()),
            "brier": float(np.square(scores - target).sum(1).mean()), "ece_10_bins": float(ece),
            "correct_at_90_count": int((correct & high).sum()),
            "correct_at_90_fraction": float((correct & high).mean()),
            "wrong_at_90_count": int((~correct & high).sum()),
            "accuracy_when_score_at_least_90": float(correct[high].mean()) if high.any() else None,
            "confusion_matrix": confusion.tolist()}


def measure(model, x, y):
    model.eval()
    with torch.no_grad():
        scores = torch.cat([model(x[i:i + 256]).softmax(1) for i in range(0, len(x), 256)]).numpy()
    return score_metrics(scores, y.numpy()), scores


def eligible(candidate, baseline):
    gates = POLICY["gates"]
    raw, previous = candidate["raw"], baseline["raw"]
    return (raw["accuracy"] >= previous["accuracy"] - gates["raw_accuracy_tolerance"]
            and candidate["clean"]["accuracy"] >= baseline["clean"]["accuracy"] - gates["clean_accuracy_tolerance"]
            and raw["correct_at_90_fraction"] >= previous["correct_at_90_fraction"] + gates["minimum_correct_90_coverage_gain"]
            and raw["loss"] < previous["loss"]
            and raw["brier"] <= previous["brier"] + gates["brier_tolerance"]
            and raw["ece_10_bins"] <= previous["ece_10_bins"] + gates["ece_tolerance"])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["train", "test"], required=True)
    args = parser.parse_args()
    directory = ROOT / "artifacts" / NAME
    report_path = ROOT / "reports" / (NAME + ".json")
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    baseline_path = ROOT / "artifacts/captcha-v3/best.pt"
    baseline = ResidualCNN()
    baseline.load_state_dict(torch.load(baseline_path, map_location="cpu", weights_only=True))
    fonts = Path("C:/Windows/Fonts")
    train_fonts = [fonts / name for name in TRAIN_FONTS + EXTRA_FONTS + ADDED_FONTS]
    dev_fonts = [fonts / name for name in DEV_FONTS]
    test_fonts = [fonts / name for name in TEST_FONTS]
    for path in train_fonts + dev_fonts + test_fonts:
        if not path.is_file():
            raise SystemExit(f"Missing font: {path.name}")
    assert not set(p.stem.lower() for p in train_fonts) & set(p.stem.lower() for p in dev_fonts + test_fonts)
    if args.stage == "train":
        if directory.exists() or report_path.exists():
            raise SystemExit("Preserve experiment; destination already exists")
        directory.mkdir(parents=True)
        metadata = {"status": "TRAINING", "started_utc": datetime.now(timezone.utc).isoformat(),
                    "architecture": ARCHITECTURE, "policy": POLICY, "history": [],
                    "baseline_checkpoint_sha256": digest(baseline_path),
                    "source_sha256": {name: digest(ROOT / "digitlab" / name) for name in
                                      ["confidence.py", "residual.py", "captcha.py", "highres.py", "ensemble_benchmark.py", "preprocess.py", "model.py", "data.py"]},
                    "font_sha256": {p.name: digest(p) for p in train_fonts + dev_fonts + test_fonts},
                    "environment": {"python": platform.python_version(), "torch": torch.__version__,
                                    "numpy": np.__version__, "pillow": pillow_version, "threads": 4}}
        write_json(report_path, metadata)
        images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
        train, validation = split_indices(labels)
        np.savez(directory / "split.npz", train=train, validation=validation)
        clean = torch.from_numpy(prepare_mnist(images, 64))
        target = torch.from_numpy(labels.astype(np.int64))
        vx, vy = clean[validation], target[validation]
        print("Preparing new independent development samples...", flush=True)
        rx, ry = make_raw(images, labels, validation, dev_fonts, POLICY["development_count"], SEED + 1)
        base = {"clean": measure(baseline, vx, vy)[0], "raw": measure(baseline, rx, ry)[0]}
        metadata["baseline_validation"] = base
        write_json(report_path, metadata)
        print(f"Baseline raw accuracy={base['raw']['accuracy']:.3%}, correct >=90 coverage={base['raw']['correct_at_90_fraction']:.3%}, NLL={base['raw']['loss']:.5f}", flush=True)
        model = ResidualCNN()
        model.load_state_dict(baseline.state_dict())
        optimizer = torch.optim.AdamW(model.parameters(), lr=.0001, weight_decay=.0001)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, POLICY["epochs"], eta_min=.000005)
        best = float("inf")
        for epoch in range(POLICY["epochs"]):
            start = time.perf_counter()
            tx, ty = make_raw(images, labels, train, train_fonts, POLICY["raw_per_epoch"], SEED + 100 + epoch)
            chosen = train[torch.randperm(len(train))[:POLICY["clean_per_epoch"]].numpy()]
            tx, ty = torch.cat([tx, clean[chosen]]), torch.cat([ty, target[chosen]])
            model.train()
            order = torch.randperm(len(tx))
            for begin in range(0, len(tx), POLICY["batch_size"]):
                batch = order[begin:begin + POLICY["batch_size"]]
                optimizer.zero_grad(set_to_none=True)
                loss = F.cross_entropy(model(augment(tx[batch])), ty[batch])
                loss.backward()
                optimizer.step()
            metrics = {"clean": measure(model, vx, vy)[0], "raw": measure(model, rx, ry)[0]}
            passes = eligible(metrics, base)
            if passes and metrics["raw"]["loss"] < best:
                best = metrics["raw"]["loss"]
                torch.save(model.state_dict(), directory / "best.pt")
                metadata.update(selected_epoch=epoch + 1, validation=metrics)
            metadata["history"].append({"epoch": epoch + 1, **metrics, "eligible": passes, "seconds": time.perf_counter() - start})
            write_json(report_path, metadata)
            print(f"Epoch {epoch + 1}/{POLICY['epochs']}: clean={metrics['clean']['accuracy']:.3%}, raw={metrics['raw']['accuracy']:.3%}, correct >=90={metrics['raw']['correct_at_90_fraction']:.3%}, NLL={metrics['raw']['loss']:.5f}, eligible={passes}, {time.perf_counter()-start:.1f}s", flush=True)
            scheduler.step()
        torch.save(model.state_dict(), directory / "last.pt")
        metadata["status"] = "SELECTED; fresh test NOT RUN" if "selected_epoch" in metadata else "RETAIN BASELINE; no eligible epoch"
        selection = {"selected_epoch": metadata.get("selected_epoch"), "policy": POLICY, "test_loaded": False,
                     "checkpoint_sha256": digest(directory / "best.pt") if "selected_epoch" in metadata else None}
        write_json(directory / "selection.json", selection)
        write_json(report_path, metadata)
        return
    metadata = json.loads(report_path.read_text())
    selection = json.loads((directory / "selection.json").read_text())
    assert selection["selected_epoch"] and "test" not in metadata
    assert digest(directory / "best.pt") == selection["checkpoint_sha256"]
    assert all(digest(ROOT / "digitlab" / name) == value for name, value in metadata["source_sha256"].items())
    with (directory / "test-started.json").open("x") as stream:
        json.dump(selection, stream)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    clean = torch.from_numpy(prepare_mnist(images, 64))
    target = torch.from_numpy(labels.astype(np.int64))
    raw, raw_y = make_raw(images, labels, np.arange(len(labels)), test_fonts, POLICY["test_count"], SEED + 2,
                         directory / "fixtures")
    model = ResidualCNN()
    model.load_state_dict(torch.load(directory / "best.pt", map_location="cpu", weights_only=True))
    results = {}
    predictions = {}
    for name, network in [("baseline", baseline), ("candidate", model)]:
        results[name] = {}
        for kind, x, y in [("clean", clean, target), ("raw", raw, raw_y)]:
            results[name][kind], predictions[name + "_" + kind] = measure(network, x, y)
    np.savez_compressed(directory / "test-predictions.npz", **predictions, labels=raw_y.numpy())
    metadata["test"] = results
    metadata["independent_test_eligible"] = eligible(results["candidate"], results["baseline"])
    metadata["status"] = "PASS: independent gates; browser/challenge NOT RUN" if metadata["independent_test_eligible"] else "RETAIN BASELINE: independent test gate failed"
    write_json(report_path, metadata)
    print(json.dumps({"status": metadata["status"], "test": results}, indent=2), flush=True)


if __name__ == "__main__":
    main()
