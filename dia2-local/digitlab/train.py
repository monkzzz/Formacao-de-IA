"""Train, select on validation loss, evaluate once and export real weights."""

import argparse
import hashlib
import json
import platform
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from .data import FILES, load_partition, split_indices
from .model import DigitCNN, augment
from .preprocess import VERSION, prepare_mnist

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


@torch.no_grad()
def evaluate(model, x, y, batch_size=512):
    model.eval()
    logits = torch.cat([model(x[i:i + batch_size]) for i in range(0, len(x), batch_size)])
    predicted = logits.argmax(1)
    confusion = torch.bincount(y * 10 + predicted, minlength=100).reshape(10, 10)
    return {"count": len(y), "loss": F.cross_entropy(logits, y).item(),
            "accuracy": (predicted == y).float().mean().item(),
            "correct": int((predicted == y).sum()), "confusion_matrix": confusion.tolist()}, logits


def export(model, metadata, test_x, test_y):
    directory = ROOT / "dist/model"
    directory.mkdir(parents=True, exist_ok=True)
    chunks, tensors, offset = [], [], 0
    for name, tensor in model.state_dict().items():
        array = tensor.detach().cpu().numpy().astype("<f4")
        chunks.append(array.tobytes())
        tensors.append({"name": name, "shape": list(array.shape), "offset": offset,
                        "length": array.size})
        offset += array.size
    weights = b"".join(chunks)
    (directory / "weights.bin").write_bytes(weights)
    manifest = {"schema": 1, "architecture": "cnn16-32-128", "preprocessing": VERSION,
                "dtype": "float32-le", "sha256": hashlib.sha256(weights).hexdigest(),
                "bytes": len(weights), "tensors": tensors, "training": metadata}
    write_json(directory / "manifest.json", manifest)
    # Digit-balanced parity examples, chosen without using challenge images.
    indices = [int(torch.nonzero(test_y == d)[0]) for d in range(10)]
    inputs = test_x[indices]
    with torch.no_grad():
        logits = model(inputs)
        first, second, hidden = model.features(inputs)
    fixture = {"absolute_tolerance": 0.0001, "model_sha256": manifest["sha256"],
               "cases": [{"input": inputs[i].flatten().tolist(), "label": int(test_y[index]),
                          "logits": logits[i].tolist(), "hidden": hidden[i].tolist(),
                          "pool1": first[i].flatten().tolist(),
                          "pool2": second[i].flatten().tolist()} for i, index in enumerate(indices)]}
    write_json(directory / "parity.json", fixture)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT.parent / "Dia2/Dataset-MNIST/data")
    parser.add_argument("--epochs", type=int, default=18)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--evaluate-only", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    artifacts, reports = ROOT / "artifacts", ROOT / "reports"
    artifacts.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    checkpoint = artifacts / "best.pt"
    model = DigitCNN()
    start = time.perf_counter()
    if not args.evaluate_only:
        if checkpoint.exists():
            raise SystemExit("Checkpoint exists. Use --evaluate-only or a separate experiment directory; do not overwrite the frozen run.")
        images, labels = load_partition(args.data, True)
        train_indices, validation_indices = split_indices(labels, args.seed)
        assert not np.intersect1d(train_indices, validation_indices).size
        np.savez(artifacts / "split.npz", train=train_indices, validation=validation_indices)
        print("Preparing all 60,000 training images with the shared image contract...", flush=True)
        x = torch.from_numpy(prepare_mnist(images))
        y = torch.from_numpy(labels.astype(np.int64))
        tx, ty, vx, vy = x[train_indices], y[train_indices], x[validation_indices], y[validation_indices]
        metadata = {"seed": args.seed, "epochs_planned": args.epochs, "batch_size": 256,
                    "optimizer": "AdamW", "learning_rate": .001, "weight_decay": .0001,
                    "split": {"train": len(tx), "validation": len(vx), "stratified": True},
                    "selection": "lowest clean validation cross-entropy", "threads": args.threads,
                    "augmentation": "affine ±0.20 radians, scale .90–1.10, translation ±.10 normalized; Gaussian sigma .025",
                    "python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__,
                    "device": "cpu", "preprocessing": VERSION,
                    "data_md5": {k: v[2] for k, v in FILES.items()}, "history": []}
        write_json(reports / "training.json", metadata)
        optimizer = torch.optim.AdamW(model.parameters(), lr=.001, weight_decay=.0001)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=.00005)
        best_loss = float("inf")
        for epoch in range(args.epochs):
            epoch_start = time.perf_counter()
            model.train()
            order = torch.randperm(len(tx))
            total_loss, total_correct = 0., 0
            for begin in range(0, len(tx), 256):
                selection = order[begin:begin + 256]
                batch, target = augment(tx[selection]), ty[selection]
                optimizer.zero_grad(set_to_none=True)
                logits = model(batch)
                loss = F.cross_entropy(logits, target)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(target)
                total_correct += int((logits.argmax(1) == target).sum())
            validation, _ = evaluate(model, vx, vy)
            record = {"epoch": epoch + 1, "train_loss": total_loss / len(tx),
                      "train_accuracy": total_correct / len(tx), "validation": validation,
                      "seconds": time.perf_counter() - epoch_start, "learning_rate": scheduler.get_last_lr()[0]}
            metadata["history"].append(record)
            if validation["loss"] < best_loss:
                best_loss = validation["loss"]
                metadata["selected_epoch"] = epoch + 1
                torch.save(model.state_dict(), checkpoint)
            write_json(reports / "training.json", metadata)
            print(f"Epoch {epoch+1:02d}/{args.epochs}: loss {record['train_loss']:.4f}, validation {validation['accuracy']:.2%}, {record['seconds']:.1f}s", flush=True)
            scheduler.step()
    else:
        metadata = json.loads((reports / "training.json").read_text(encoding="utf-8"))
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    model.eval()
    print("Selected model frozen; loading the official test partition for evaluation.", flush=True)
    test_images, test_labels = load_partition(args.data, False)
    test_x = torch.from_numpy(prepare_mnist(test_images))
    test_y = torch.from_numpy(test_labels.astype(np.int64))
    test_metrics, test_logits = evaluate(model, test_x, test_y)
    metadata["test"] = test_metrics
    manifest = export(model, metadata, test_x, test_y)
    wrong = torch.nonzero(test_logits.argmax(1) != test_y).flatten().tolist()
    test_metrics.update({"model_sha256": manifest["sha256"], "preprocessing": VERSION,
                         "selected_epoch": metadata["selected_epoch"], "error_indices": wrong,
                         "elapsed_seconds": time.perf_counter() - start})
    write_json(reports / "mnist-test.json", test_metrics)
    # A small clean-MNIST image set for browser upload tests, never challenge inputs.
    from PIL import Image
    fixtures = reports / "mnist-fixtures"
    fixtures.mkdir(exist_ok=True)
    for digit in range(10):
        index = int(np.flatnonzero(test_labels == digit)[0])
        Image.fromarray(test_images[index]).save(fixtures / f"digit-{digit}.png")
    print(json.dumps({"mnist_test": test_metrics["accuracy"], "correct": test_metrics["correct"],
                      "model_sha256": manifest["sha256"]}), flush=True)


if __name__ == "__main__":
    main()
