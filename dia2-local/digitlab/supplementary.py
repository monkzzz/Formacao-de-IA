"""Separate MNIST + EMNIST Digits experiment; never replace preserved models."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
import time

import numpy as np
import torch
from torch.nn import functional as F

from . import supplementary_data as extra
from .confidence import measure
from .confidence_broad import font_groups
from .data import load_partition, split_indices
from .model import DigitCNN, augment
from .preprocess import VERSION, prepare_mnist
from .highres import make_raw
from .train import ROOT, write_json

NAME = "mnist-supplementary-v1"
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
DESTINATION = ROOT / "dist/model" / NAME / "digits"
SEED = 2026102001
POLICY = {"seed": SEED, "epochs": 4, "batch_size": 256, "threads": 4,
          "learning_rate": .0002, "minimum_learning_rate": .00002,
          "weight_decay": .0001, "synthetic_training_count": 12000,
          "synthetic_validation_count": 2400, "synthetic_test_count": 2400,
          "selection": "Minimum equal-weight mean NLL across MNIST, EMNIST and synthetic validation; freeze before test metrics",
          "role": "Optional supplementary-data experiment; not the required MNIST-only submission or a qualified default replacement",
          "official_challenge_used": False, "official_challenge_evaluation": "NOT RUN",
          "test_hygiene": "Test pixels fingerprinted only before training for exact duplicate exclusion; no test labels or metrics used for selection",
          "limitations": "No writer-disjoint or near-duplicate independence claim; synthetic examples are not collected real CAPTCHAs"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def original_model():
    """Recover only the original MNIST-only network, preserving its exact weights."""
    folder = ROOT / "dist/model"
    manifest = json.loads((folder / "manifest.json").read_text())
    blob = (folder / "weights.bin").read_bytes()
    if digest(folder / "weights.bin") != manifest["sha256"] or len(blob) != manifest["bytes"]:
        raise ValueError("Original MNIST weights failed verification")
    model = DigitCNN()
    state = model.state_dict()
    cursor = 0
    for name, tensor in state.items():
        spec = next(t for t in manifest["tensors"] if t["name"] == name)
        if spec["shape"] != list(tensor.shape) or spec["length"] != tensor.numel() or spec["offset"] != cursor:
            raise ValueError("Original model tensor contract mismatch")
        state[name] = torch.from_numpy(np.frombuffer(blob, "<f4", count=tensor.numel(), offset=4 * cursor).copy().reshape(tensor.shape))
        cursor += tensor.numel()
    if cursor * 4 != len(blob):
        raise ValueError("Unexpected original model payload")
    model.load_state_dict(state)
    return model


def export(model, metadata, inputs):
    DESTINATION.mkdir(parents=True, exist_ok=False)
    chunks, tensors, cursor = [], [], 0
    for name, tensor in model.state_dict().items():
        array = tensor.detach().numpy().astype("<f4")
        chunks.append(array.tobytes())
        tensors.append({"name": name, "shape": list(array.shape), "length": array.size, "offset": cursor})
        cursor += array.size
    blob = b"".join(chunks)
    (DESTINATION / "weights.bin").write_bytes(blob)
    manifest = {"schema": 1, "architecture": "cnn16-32-128", "task": "digits", "labels": list("0123456789"),
                "preprocessing": VERSION, "dtype": "float32-le", "sha256": hashlib.sha256(blob).hexdigest(),
                "bytes": len(blob), "tensors": tensors, "training": metadata,
                "dataset_role": "supplementary", "training_sources": ["MNIST", "EMNIST Digits", "independent synthetic CAPTCHA-style examples"]}
    write_json(DESTINATION / "manifest.json", manifest)
    model.eval()
    with torch.no_grad():
        logits = model(inputs)
        first, second, hidden = model.features(inputs)
    write_json(DESTINATION / "parity.json", {"model_sha256": manifest["sha256"], "absolute_tolerance": .0001,
        "cases": [{"input": inputs[i].flatten().tolist(), "logits": logits[i].tolist(),
                   "pool1": first[i].flatten().tolist(), "pool2": second[i].flatten().tolist(),
                   "hidden": hidden[i].tolist()} for i in range(len(inputs))]})
    return manifest


def run():
    if DIRECTORY.exists() or REPORT.exists() or DESTINATION.exists():
        raise ValueError("Preserve completed supplementary experiment; do not overwrite")
    DIRECTORY.mkdir(parents=True)
    torch.set_num_threads(POLICY["threads"])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    preserved = {str(p.relative_to(ROOT)): digest(p) for folder in (ROOT / "dist/model", ROOT / "dist/model/captcha-v3/digits")
                 for p in folder.glob("*") if p.is_file()}
    provenance = extra.extract()
    print("Verified EMNIST archive; loading independent source partitions...", flush=True)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    # Reserve test fingerprints solely for data hygiene, never test scores/labels for selection.
    test_images, _ = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    e_images, e_labels = extra.load_partition(True)
    e_test_images, _ = extra.load_partition(False)
    mnist_hashes = set(extra.fingerprints(images)) | set(extra.fingerprints(test_images))
    excluded = mnist_hashes | set(extra.fingerprints(e_test_images))
    kept = extra.unique_indices(e_images, excluded)
    e_train, e_val = extra.stratified_split(e_labels, kept)
    e_test_kept = extra.unique_indices(e_test_images, mnist_hashes)
    train, validation = split_indices(labels)
    np.savez(DIRECTORY / "split.npz", mnist_train=train, mnist_validation=validation,
             emnist_train=e_train, emnist_validation=e_val, emnist_test=e_test_kept)
    del test_images, e_test_images
    fonts = font_groups(ROOT / "data/open-fonts")
    metadata = {"status": "PREPARING", "started_utc": datetime.now(timezone.utc).isoformat(),
        "policy": POLICY, "split": {"train": len(train) + len(e_train), "validation": len(validation) + len(e_val)},
        "source_counts": {"mnist_train": len(train), "mnist_validation": len(validation),
                          "emnist_train": len(e_train), "emnist_validation": len(e_val), "emnist_test_after_exact_dedup": len(e_test_kept),
                          "emnist_train_duplicates_or_reserved_overlap_removed": len(e_images) - len(kept)},
        "sources": provenance, "preserved": preserved, "history": [],
        "source_sha256": {name: digest(ROOT / "digitlab" / name) for name in
                          ("supplementary.py", "supplementary_data.py", "model.py", "preprocess.py", "highres.py", "captcha.py")},
        "split_sha256": digest(DIRECTORY / "split.npz"),
        "environment": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__, "platform": platform.platform()},
        "fonts_sha256": {str(p.relative_to(ROOT)): digest(p) for group in fonts.values() for p in group}}
    write_json(REPORT, metadata)
    print("Preparing MNIST, supplementary handwriting and independent raw examples...", flush=True)
    clean = torch.from_numpy(prepare_mnist(images))
    e_clean = torch.from_numpy(prepare_mnist(e_images[kept]))
    # Map original source indices into the compact preprocessed cache.
    positions = {int(index): position for position, index in enumerate(kept)}
    et = np.array([positions[int(i)] for i in e_train])
    ev = np.array([positions[int(i)] for i in e_val])
    target = torch.from_numpy(labels.astype(np.int64))
    e_target = torch.from_numpy(e_labels[kept].astype(np.int64))
    _, raw_x, raw_y = make_raw(e_images, e_labels, e_train, fonts["train"], POLICY["synthetic_training_count"], SEED + 1)
    _, raw_vx, raw_vy = make_raw(e_images, e_labels, e_val, fonts["development"], POLICY["synthetic_validation_count"], SEED + 2)
    vx = {"mnist": (clean[validation], target[validation]), "emnist": (e_clean[ev], e_target[ev]), "synthetic": (raw_vx, raw_vy)}
    model = original_model()
    metadata["baseline_validation"] = {k: measure(model, *v)[0] for k, v in vx.items()}
    tx = torch.cat((clean[train], e_clean[et], raw_x))
    ty = torch.cat((target[train], e_target[et], raw_y))
    metadata["training_examples_per_epoch"] = len(tx)
    metadata["status"] = "TRAINING"
    write_json(REPORT, metadata)
    del e_clean, raw_x
    optimizer = torch.optim.AdamW(model.parameters(), lr=POLICY["learning_rate"], weight_decay=POLICY["weight_decay"])
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, POLICY["epochs"], eta_min=POLICY["minimum_learning_rate"])
    best = float("inf")
    for epoch in range(POLICY["epochs"]):
        start = time.perf_counter()
        model.train()
        order = torch.randperm(len(tx))
        for begin in range(0, len(tx), POLICY["batch_size"]):
            ids = order[begin:begin + POLICY["batch_size"]]
            optimizer.zero_grad(set_to_none=True)
            F.cross_entropy(model(augment(tx[ids])), ty[ids]).backward()
            optimizer.step()
        metrics = {key: measure(model, *data)[0] for key, data in vx.items()}
        objective = sum(m["loss"] for m in metrics.values()) / len(metrics)
        if objective < best:
            best = objective
            torch.save(model.state_dict(), DIRECTORY / "best.pt")
            metadata.update(selected_epoch=epoch + 1, validation=metrics)
        metadata["history"].append({"epoch": epoch + 1, "validation": metrics, "selection_loss": objective, "seconds": time.perf_counter() - start})
        write_json(REPORT, metadata)
        print(f"Epoch {epoch+1}: MNIST={metrics['mnist']['accuracy']:.3%}, EMNIST={metrics['emnist']['accuracy']:.3%}, synthetic={metrics['synthetic']['accuracy']:.3%}, {time.perf_counter()-start:.1f}s", flush=True)
        schedule.step()
    selection = {"selected_epoch": metadata["selected_epoch"], "checkpoint_sha256": digest(DIRECTORY / "best.pt"),
                 "policy": POLICY, "test_metrics_loaded": False, "source_sha256": metadata["source_sha256"]}
    write_json(DIRECTORY / "selection.json", selection)
    model.load_state_dict(torch.load(DIRECTORY / "best.pt", map_location="cpu", weights_only=True))
    print("Selection frozen. Evaluating both models on reserved partitions...", flush=True)
    test_images, test_labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    e_test_images, e_test_labels = extra.load_partition(False)
    test_x, test_y = torch.from_numpy(prepare_mnist(test_images)), torch.from_numpy(test_labels.astype(np.int64))
    e_test_x = torch.from_numpy(prepare_mnist(e_test_images[e_test_kept]))
    e_test_y = torch.from_numpy(e_test_labels[e_test_kept].astype(np.int64))
    _, raw_tx, raw_ty = make_raw(e_test_images, e_test_labels, e_test_kept, fonts["test"], POLICY["synthetic_test_count"], SEED + 3, DIRECTORY / "fixtures")
    tests = {"mnist": (test_x, test_y), "emnist": (e_test_x, e_test_y), "synthetic": (raw_tx, raw_ty)}
    metadata["evaluation"] = {}
    vectors = {}
    for name, network in (("mnist_only", original_model()), ("supplementary", model)):
        metadata["evaluation"][name] = {}
        for group, data in tests.items():
            metrics, logits = measure(network, *data)
            metadata["evaluation"][name][group] = metrics
            vectors[name + "_" + group] = logits
    np.savez_compressed(DIRECTORY / "test-predictions.npz", **vectors)
    metadata["test"] = metadata["evaluation"]["supplementary"]["mnist"]
    metadata["status"] = "TRAINED; optional extension; official challenge NOT RUN"
    metadata["completed_utc"] = datetime.now(timezone.utc).isoformat()
    metadata["preservation_pass"] = all(digest(ROOT / p) == h for p, h in preserved.items())
    if not metadata["preservation_pass"]:
        raise ValueError("Preserved model changed")
    fixture_ids = [int(torch.nonzero(target[validation] == digit)[0]) for digit in range(10)]
    manifest = export(model, metadata, clean[validation][fixture_ids])
    metadata["model_sha256"] = manifest["sha256"]
    write_json(REPORT, metadata)
    print(json.dumps({"status": metadata["status"], "sha256": manifest["sha256"], "test": metadata["test"]}), flush=True)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()


if __name__ == "__main__":
    main()
