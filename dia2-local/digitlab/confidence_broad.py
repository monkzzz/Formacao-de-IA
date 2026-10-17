"""Bounded portable confidence experiment; official inputs are never loaded."""

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import time

import numpy as np
from PIL import __version__ as pillow_version
import torch
from torch.nn import functional as F

from .confidence import POLICY as ORIGINAL_POLICY, digest, eligible, measure
from .data import load_partition, split_indices
from .model import augment
from .preprocess import prepare_mnist
from .residual import ResidualCNN, make_raw
from .train import ROOT, write_json

NAME = "captcha-confidence-broad-v1"
SEED = 2026101801
POLICY = {
    "seed": SEED, "epochs": 8, "raw_per_epoch": 24000,
    "clean_per_epoch": 12000, "development_count": 6000, "test_count": 10000,
    "batch_size": 128, "threads": 4, "learning_rate": .0001,
    "minimum_learning_rate": .00001, "weight_decay": .0001,
    "ema_decay": .99, "training_dropout": .1,
    "objective": "Unmodified cross entropy; original preprocessing and raw softmax",
    "selection": "Minimum development raw NLL among eligible EMA epoch checkpoints",
    "gates": ORIGINAL_POLICY["gates"],
    "font_split": "Open-font bundle: train NotoSans/NotoSerif/RobotoSlab/Oswald; develop Lato; test Ubuntu",
    "prior_exposure": "New synthetic seeds and current-run font splits; baseline has prior evaluations. Not a blind real-CAPTCHA study.",
    "official_inputs_used": False, "temperature": 1.0,
}
SOURCES = ("confidence_broad.py", "confidence.py", "residual.py", "highres.py",
           "captcha.py", "ensemble_benchmark.py", "model.py", "preprocess.py", "data.py", "platform_support.py")


def font_groups(root):
    manifest = json.loads((root / "font-groups.json").read_text())
    groups = {key: [root / name for name in manifest["groups"][key]]
              for key in ("train", "development", "test")}
    for name, expected in manifest["sha256"].items():
        if digest(root / name) != expected:
            raise ValueError(f"Font bundle identity changed: {name}")
    hashes = [{digest(p) for p in paths} for paths in groups.values()]
    if any(not values for values in hashes) or any(hashes[i] & hashes[j] for i in range(3) for j in range(i)):
        raise ValueError("Font groups must be nonempty and disjoint")
    return groups


@torch.no_grad()
def update_average(average, model, decay):
    for current, source in zip(average.parameters(), model.parameters()):
        current.lerp_(source, 1 - decay)


def load_model(path):
    model = ResidualCNN()
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("train", "test"), required=True)
    parser.add_argument("--font-root", type=Path, default=ROOT / "data/open-fonts")
    args = parser.parse_args()
    torch.set_num_threads(POLICY["threads"])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    fonts = font_groups(args.font_root)
    directory = ROOT / "artifacts" / NAME
    output = ROOT / "reports" / (NAME + ".json")
    baseline_path = ROOT / "artifacts/captcha-v3/best.pt"
    baseline = load_model(baseline_path)
    # Verify that the checkpoint really matches the preserved browser model.
    exported = b"".join(t.detach().numpy().astype("<f4").tobytes()
                        for t in baseline.state_dict().values())
    import hashlib
    manifest = json.loads((ROOT / "dist/model/captcha-v3/digits/manifest.json").read_text())
    if hashlib.sha256(exported).hexdigest() != manifest["sha256"]:
        raise ValueError("Baseline checkpoint/browser export mismatch")
    if args.stage == "train":
        directory.mkdir(parents=True, exist_ok=False)
        if output.exists():
            raise FileExistsError(output)
        metadata = {
            "status": "TRAINING", "started_utc": datetime.now(timezone.utc).isoformat(),
            "policy": POLICY, "history": [],
            "baseline_checkpoint_sha256": digest(baseline_path),
            "baseline_export_sha256": manifest["sha256"],
            "source_sha256": {n: digest(ROOT / "digitlab" / n) for n in SOURCES},
            "fonts": {k: {str(p): digest(p) for p in v} for k, v in fonts.items()},
            "environment": {"python": platform.python_version(), "torch": torch.__version__,
                            "numpy": np.__version__, "pillow": pillow_version,
                            "platform": platform.platform(), "threads": POLICY["threads"]},
        }
        write_json(output, metadata)
        images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
        train, validation = split_indices(labels)
        np.savez(directory / "split.npz", train=train, validation=validation)
        metadata["split_sha256"] = digest(directory / "split.npz")
        clean_ids = np.random.default_rng(SEED).choice(train, POLICY["clean_per_epoch"], replace=False)
        clean = torch.from_numpy(prepare_mnist(images[clean_ids], 64))
        clean_y = torch.from_numpy(labels[clean_ids].astype(np.int64))
        vx = torch.from_numpy(prepare_mnist(images[validation], 64))
        vy = torch.from_numpy(labels[validation].astype(np.int64))
        print("Generating new independent Lato development set...", flush=True)
        rx, ry = make_raw(images, labels, validation, fonts["development"],
                          POLICY["development_count"], SEED + 1)
        base = {"clean": measure(baseline, vx, vy)[0], "raw": measure(baseline, rx, ry)[0]}
        metadata["baseline_validation"] = base
        write_json(output, metadata)
        print(f"Baseline raw={base['raw']['accuracy']:.3%}, correct-at-90={base['raw']['correct_at_90_fraction']:.3%}, NLL={base['raw']['loss']:.5f}", flush=True)
        model = copy.deepcopy(baseline)
        model.dropout.p = POLICY["training_dropout"]
        average = copy.deepcopy(baseline)
        optimizer = torch.optim.AdamW(model.parameters(), lr=POLICY["learning_rate"],
                                     weight_decay=POLICY["weight_decay"])
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, POLICY["epochs"], eta_min=POLICY["minimum_learning_rate"])
        best = float("inf")
        for epoch in range(POLICY["epochs"]):
            started = time.perf_counter()
            tx, ty = make_raw(images, labels, train, fonts["train"],
                              POLICY["raw_per_epoch"], SEED + 100 + epoch)
            tx, ty = torch.cat((tx, clean)), torch.cat((ty, clean_y))
            model.train()
            order = torch.randperm(len(tx))
            for begin in range(0, len(tx), POLICY["batch_size"]):
                ids = order[begin:begin + POLICY["batch_size"]]
                optimizer.zero_grad(set_to_none=True)
                F.cross_entropy(model(augment(tx[ids])), ty[ids]).backward()
                optimizer.step()
                update_average(average, model, POLICY["ema_decay"])
            metrics = {"clean": measure(average, vx, vy)[0], "raw": measure(average, rx, ry)[0]}
            passes = eligible(metrics, base)
            if passes and metrics["raw"]["loss"] < best:
                best = metrics["raw"]["loss"]
                torch.save(average.state_dict(), directory / "best.pt")
                metadata.update(selected_epoch=epoch + 1, validation=metrics)
            metadata["history"].append({"epoch": epoch + 1, **metrics,
                                        "eligible": passes, "seconds": time.perf_counter() - started})
            write_json(output, metadata)
            print(f"Epoch {epoch+1}: clean={metrics['clean']['accuracy']:.3%}, raw={metrics['raw']['accuracy']:.3%}, correct-at-90={metrics['raw']['correct_at_90_fraction']:.3%}, NLL={metrics['raw']['loss']:.5f}, eligible={passes}, {time.perf_counter()-started:.1f}s", flush=True)
            scheduler.step()
            del tx, ty
        torch.save(average.state_dict(), directory / "last.pt")
        selection = {"selected_epoch": metadata.get("selected_epoch"), "policy": POLICY,
                     "test_loaded": False, "checkpoint_sha256": digest(directory / "best.pt")
                     if "selected_epoch" in metadata else None,
                     "source_sha256": metadata["source_sha256"]}
        write_json(directory / "selection.json", selection)
        metadata["status"] = "SELECTED; test NOT RUN" if selection["selected_epoch"] else "RETAIN BASELINE; no eligible epoch"
        metadata["completed_utc"] = datetime.now(timezone.utc).isoformat()
        if digest(baseline_path) != metadata["baseline_checkpoint_sha256"]:
            raise ValueError("Baseline changed")
        write_json(output, metadata)
        print(metadata["status"], flush=True)
        return

    metadata = json.loads(output.read_text())
    selection = json.loads((directory / "selection.json").read_text())
    if not selection["selected_epoch"] or "test" in metadata:
        raise ValueError("Test requires eligible frozen selection and no prior test")
    if digest(directory / "best.pt") != selection["checkpoint_sha256"]:
        raise ValueError("Selected checkpoint changed")
    if digest(baseline_path) != metadata["baseline_checkpoint_sha256"]:
        raise ValueError("Baseline changed")
    if any(digest(ROOT / "digitlab" / n) != h for n, h in selection["source_sha256"].items()):
        raise ValueError("Experiment sources changed after selection")
    if any(digest(Path(p)) != h for group in metadata["fonts"].values() for p, h in group.items()):
        raise ValueError("Experiment fonts changed")
    with (directory / "test-started.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    clean = torch.from_numpy(prepare_mnist(images, 64))
    clean_y = torch.from_numpy(labels.astype(np.int64))
    rx, ry = make_raw(images, labels, np.arange(len(labels)), fonts["test"],
                      POLICY["test_count"], SEED + 2, directory / "fixtures")
    candidate = load_model(directory / "best.pt")
    results, predictions = {}, {}
    for name, network in (("baseline", baseline), ("candidate", candidate)):
        results[name] = {}
        for kind, x, y in (("clean", clean, clean_y), ("raw", rx, ry)):
            results[name][kind], predictions[name + "_" + kind] = measure(network, x, y)
    np.savez_compressed(directory / "test-predictions.npz", **predictions,
                        raw_labels=ry.numpy(), clean_labels=clean_y.numpy())
    metadata["test"] = results
    metadata["independent_test_eligible"] = eligible(results["candidate"], results["baseline"])
    metadata["status"] = ("PASS: independent gates; browser/challenge NOT RUN"
                          if metadata["independent_test_eligible"] else "RETAIN BASELINE: test gate failed")
    write_json(output, metadata)
    print(json.dumps({"status": metadata["status"], "test": results}, indent=2))


if __name__ == "__main__":
    main()
