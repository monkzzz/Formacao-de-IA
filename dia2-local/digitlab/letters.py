"""Train a dedicated A–Z classifier while preserving the frozen digit model."""

import argparse
import hashlib
import json
import platform
import string
import time

import numpy as np
import torch
from PIL import Image, ImageDraw
from torch import nn
from torch.nn import functional as F

from .emnist_data import DIRECTORY, load_partition
from .model import DigitCNN, augment
from .preprocess import VERSION, prepare
from .train import ROOT, write_json

LABELS = list(string.ascii_uppercase)


class LetterCNN(DigitCNN):
    """Same spatial feature layout, with 26 letter-specific output logits."""

    def __init__(self):
        super().__init__()
        self.fc2 = nn.Linear(128, 26)


def split_indices(labels, seed=20261017):
    rng = np.random.default_rng(seed)
    training, validation = [], []
    for label in range(26):
        indices = rng.permutation(np.flatnonzero(labels == label))
        validation.extend(indices[:400]); training.extend(indices[400:])
    return rng.permutation(training), rng.permutation(validation)


def prepare_images(images):
    prepared = np.empty((len(images), 1, 28, 28), dtype=np.float32)
    blank_indices = []
    for index, image in enumerate(images):
        rgba = np.empty((28, 28, 4), dtype=np.uint8)
        rgba[:, :, :3] = image[:, :, None]; rgba[:, :, 3] = 255
        try:
            prepared[index] = prepare(rgba)
        except ValueError:
            # Keep every official example in evaluation, including unreadable glyphs.
            # The website rejects such images; the benchmark counts the zero-input prediction.
            prepared[index] = 0
            blank_indices.append(index)
    return prepared, blank_indices


@torch.no_grad()
def evaluate(model, x, y):
    model.eval()
    logits = torch.cat([model(x[i:i + 512]) for i in range(0, len(x), 512)])
    predictions = logits.argmax(1)
    matrix = torch.bincount(y * 26 + predictions, minlength=676).reshape(26, 26)
    return {"count": len(y), "correct": int((predictions == y).sum()),
            "accuracy": int((predictions == y).sum()) / len(y),
            "loss": float(F.cross_entropy(logits, y)), "confusion_matrix": matrix.tolist()}, logits


def export(model, metadata, test_x, test_y, originals):
    directory = ROOT / "dist/model/letters"
    directory.mkdir(parents=True, exist_ok=True)
    chunks, tensors, offset = [], [], 0
    for name, tensor in model.state_dict().items():
        values = tensor.detach().numpy().astype("<f4")
        chunks.append(values.tobytes())
        tensors.append({"name": name, "shape": list(values.shape), "offset": offset, "length": values.size})
        offset += values.size
    weights = b"".join(chunks)
    (directory / "weights.bin").write_bytes(weights)
    manifest = {"schema": 1, "architecture": "cnn16-32-128", "task": "letters",
                "labels": LABELS, "preprocessing": VERSION, "dtype": "float32-le",
                "sha256": hashlib.sha256(weights).hexdigest(), "bytes": len(weights),
                "tensors": tensors, "training": metadata}
    write_json(directory / "manifest.json", manifest)
    indices = [int(torch.nonzero(test_y == i)[0]) for i in range(26)]
    inputs = test_x[indices]
    with torch.no_grad():
        logits = model(inputs)
        first, second, hidden = model.features(inputs)
    write_json(directory / "parity.json", {"absolute_tolerance": .0001,
        "model_sha256": manifest["sha256"], "cases": [{"label": LABELS[i],
        "input": inputs[i].flatten().tolist(), "logits": logits[i].tolist(),
        "hidden": hidden[i].tolist(), "pool1": first[i].flatten().tolist(),
        "pool2": second[i].flatten().tolist()} for i in range(26)]})
    fixtures = ROOT / "reports/letter-fixtures"
    fixtures.mkdir(exist_ok=True)
    for label, index in zip(LABELS, indices):
        Image.fromarray(originals[index]).save(fixtures / f"letter-{label}.png")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=24)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261017)
    artifact = ROOT / "artifacts/letters"
    artifact.mkdir(exist_ok=True)
    checkpoint = artifact / "best.pt"
    if checkpoint.exists():
        raise SystemExit("Letter checkpoint exists. Preserve the experiment; do not silently overwrite it.")
    start = time.perf_counter()
    images, labels = load_partition(True)
    # An upright training-only sample sheet supports checking the storage orientation.
    sheet = Image.new("RGB", (13 * 60, 2 * 80), "white")
    draw = ImageDraw.Draw(sheet)
    for i, label in enumerate(LABELS):
        image = Image.fromarray(images[np.flatnonzero(labels == i)[0]]).resize((56, 56))
        x, y = i % 13 * 60, i // 13 * 80
        sheet.paste(image, (x, y)); draw.text((x + 22, y + 58), label, fill="black")
    sheet.save(ROOT / "reports/letters-training-orientation.png")
    train_indices, validation_indices = split_indices(labels)
    assert len(train_indices) == 114400 and len(validation_indices) == 10400
    assert not np.intersect1d(train_indices, validation_indices).size
    np.savez(artifact / "split.npz", train=train_indices, validation=validation_indices)
    print("Preparing 124,800 upright training letters with the shared image contract...", flush=True)
    prepared, blanks = prepare_images(images)
    x, y = torch.from_numpy(prepared), torch.from_numpy(labels)
    tx, ty, vx, vy = x[train_indices], y[train_indices], x[validation_indices], y[validation_indices]
    provenance = json.loads((DIRECTORY / "provenance.json").read_text(encoding="utf-8"))
    metadata = {"dataset": "EMNIST Letters", "labels": LABELS, "case_policy": "uppercase/lowercase merged into A–Z",
                "seed": 20261017, "epochs_planned": args.epochs, "batch_size": 256,
                "optimizer": "AdamW", "learning_rate": .001, "weight_decay": .0001,
                "augmentation": "training-only affine ±0.20 radians, scale .90–1.10, translation ±.10 normalized, Gaussian sigma .025",
                "split": {"train": len(tx), "validation": len(vx), "validation_per_class": 400},
                "orientation": "transpose raw image axes; no inference-time rotation",
                "selection": "minimum clean validation cross-entropy", "provenance": provenance,
                "python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__,
                "device": "cpu", "threads": args.threads, "preprocessing": VERSION,
                "unreadable_train_indices": blanks, "history": []}
    model = LetterCNN()
    optimizer = torch.optim.AdamW(model.parameters(), lr=.001, weight_decay=.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=.00005)
    best = float("inf")
    for epoch in range(args.epochs):
        epoch_start = time.perf_counter()
        model.train()
        order = torch.randperm(len(tx))
        loss_sum, correct = 0., 0
        for begin in range(0, len(tx), 256):
            indices = order[begin:begin + 256]
            batch, target = augment(tx[indices]), ty[indices]
            optimizer.zero_grad(set_to_none=True)
            logits = model(batch)
            loss = F.cross_entropy(logits, target)
            loss.backward(); optimizer.step()
            loss_sum += float(loss.detach()) * len(target)
            correct += int((logits.argmax(1) == target).sum())
        validation, _ = evaluate(model, vx, vy)
        record = {"epoch": epoch + 1, "train_loss": loss_sum / len(tx),
                  "train_accuracy": correct / len(tx), "validation": validation,
                  "seconds": time.perf_counter() - epoch_start, "learning_rate": scheduler.get_last_lr()[0]}
        metadata["history"].append(record)
        if validation["loss"] < best:
            best = validation["loss"]; metadata["selected_epoch"] = epoch + 1
            torch.save(model.state_dict(), checkpoint)
        write_json(ROOT / "reports/letters-training.json", metadata)
        print(f"Letters {epoch+1:02d}/{args.epochs}: loss {record['train_loss']:.4f}, validation {validation['accuracy']:.2%}, {record['seconds']:.1f}s", flush=True)
        scheduler.step()
    model.load_state_dict(torch.load(checkpoint, weights_only=True, map_location="cpu"))
    model.eval()
    print("Letter model selected and frozen. Loading 20,800 official test examples...", flush=True)
    test_images, test_labels = load_partition(False)
    test_prepared, test_blanks = prepare_images(test_images)
    test_x, test_y = torch.from_numpy(test_prepared), torch.from_numpy(test_labels)
    metrics, logits = evaluate(model, test_x, test_y)
    metadata["test"] = metrics
    manifest = export(model, metadata, test_x, test_y, test_images)
    metrics.update({"model_sha256": manifest["sha256"], "labels": LABELS,
                    "selected_epoch": metadata["selected_epoch"], "unreadable_test_indices": test_blanks,
                    "error_indices": torch.nonzero(logits.argmax(1) != test_y).flatten().tolist(),
                    "elapsed_seconds": time.perf_counter() - start})
    write_json(ROOT / "reports/letters-test.json", metrics)
    print(json.dumps({"letters_test_accuracy": metrics["accuracy"], "correct": metrics["correct"],
                      "total": metrics["count"], "sha256": manifest["sha256"]}), flush=True)


if __name__ == "__main__":
    main()
