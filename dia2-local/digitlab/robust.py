"""Train and evaluate independent robustness candidates without challenge data.

The original checkpoints, exports and first-run reports are never replaced.
Selection uses the original training/validation split, not official test data.
"""

import argparse
import hashlib
import math
import time

import numpy as np
import torch
from torch.nn import functional as F

from .data import load_partition, split_indices
from .letters import LetterCNN, LABELS, prepare_images, split_indices as letter_split
from .model import DigitCNN
from .preprocess import VERSION, prepare_mnist
from .train import ROOT, write_json

SEED = 20261018
POLICY = {
    "augmentation": "affine/shear, smooth elastic displacement, varied stroke width, sparse ink and short occlusions",
    "selection": "minimum mean clean/noisy validation cross-entropy, subject to clean accuracy floor and noisy accuracy gain",
    "clean_accuracy_tolerance": {"digits": .002, "letters": .004},
    "validation_noise_seed": SEED + 1,
    "test_noise_seed": SEED + 2,
    "challenge_inputs_used": False,
}


def distort(x):
    """Random label-preserving handwriting/scan variation on CPU tensors.

    No flips or quarter turns: these can change a digit or letter's class.
    Half the batch avoids ink interference to retain clean handwriting skill.
    """
    n = len(x)
    angle = (torch.rand(n) * 2 - 1) * .20
    scale = .90 + torch.rand(n) * .20
    shear = (torch.rand(n) * 2 - 1) * .16
    theta = torch.zeros(n, 2, 3)
    theta[:, 0, 0] = angle.cos() * scale
    theta[:, 0, 1] = -angle.sin() * scale + shear
    theta[:, 1, 0] = angle.sin() * scale
    theta[:, 1, 1] = angle.cos() * scale
    theta[:, :, 2] = (torch.rand(n, 2) * 2 - 1) * .10
    grid = F.affine_grid(theta, x.shape, align_corners=False)
    displacement = F.interpolate(torch.randn(n, 2, 4, 4), (28, 28), mode="bicubic", align_corners=False)
    grid = grid + displacement.permute(0, 2, 3, 1) * .025
    result = F.grid_sample(x, grid, align_corners=False)

    # Blend morphology rather than deleting thin strokes outright.
    width = torch.rand(n, 1, 1, 1)
    thicker = F.max_pool2d(result, 3, stride=1, padding=1)
    thinner = -F.max_pool2d(-result, 3, stride=1, padding=1)
    result = torch.where(width < .20, .65 * result + .35 * thicker, result)
    result = torch.where(width > .80, .75 * result + .25 * thinner, result)

    yy = torch.arange(28)[None, :, None]
    xx = torch.arange(28)[None, None, :]
    phase = torch.rand(n, 1, 1) * (2 * math.pi)
    line_y = 4 + torch.rand(n, 1, 1) * 20 + torch.sin(xx / 5 + phase) * 2
    line = (yy - line_y).abs() < .55
    interference = (torch.rand(n, 1, 1) < .35) * (.20 + torch.rand(n, 1, 1) * .45)
    result = torch.maximum(result, (line * interference)[:, None])
    # Short gaps and sparse speckles, rather than removing a whole stroke.
    cx, cy = torch.randint(5, 23, (2, n, 1, 1))
    gap = ((xx - cx).abs() <= 2) & ((yy - cy).abs() < 1)
    erase = gap & (torch.rand(n, 1, 1) < .25)
    result = result * (1 - erase[:, None].float() * .8)
    speckles = (torch.rand_like(result) < .003) * torch.rand_like(result) * .5
    return (result + speckles + torch.randn_like(result) * .025).clamp(0, 1)


def noisy_copy(x, seed):
    """Fixed evaluation corruption without consuming the training RNG."""
    with torch.random.fork_rng():
        torch.manual_seed(seed)
        return torch.cat([distort(x[i:i + 256]) for i in range(0, len(x), 256)])


@torch.no_grad()
def evaluate(model, x, y):
    model.eval()
    logits = torch.cat([model(x[i:i + 512]) for i in range(0, len(x), 512)])
    predicted = logits.argmax(1)
    classes = logits.shape[1]
    return {"count": len(y), "correct": int((predicted == y).sum()),
            "accuracy": float((predicted == y).double().mean()),
            "loss": float(F.cross_entropy(logits, y)),
            "confusion_matrix": torch.bincount(y * classes + predicted,
                minlength=classes * classes).reshape(classes, classes).tolist()}


def qualifies(baseline, clean, noisy, tolerance):
    return (clean["accuracy"] >= baseline["clean"]["accuracy"] - tolerance
            and noisy["accuracy"] > baseline["noisy"]["accuracy"])


def export(model, directory, metadata, inputs, labels):
    """Keep the existing browser architecture and export activation parity data."""
    chunks, tensors, offset = [], [], 0
    for name, tensor in model.state_dict().items():
        values = tensor.detach().cpu().numpy().astype("<f4")
        chunks.append(values.tobytes())
        tensors.append({"name": name, "shape": list(values.shape), "offset": offset, "length": values.size})
        offset += values.size
    blob = b"".join(chunks)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "weights.bin").write_bytes(blob)
    manifest = {"schema": 1, "architecture": "cnn16-32-128", "task": metadata["task"],
                "labels": labels, "preprocessing": VERSION, "dtype": "float32-le",
                "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
                "tensors": tensors, "training": metadata}
    write_json(directory / "manifest.json", manifest)
    model.eval()
    with torch.no_grad():
        logits = model(inputs)
        first, second, hidden = model.features(inputs)
    write_json(directory / "parity.json", {"absolute_tolerance": .0001,
        "model_sha256": manifest["sha256"], "cases": [{"label": labels[i],
        "input": inputs[i].flatten().tolist(), "logits": logits[i].tolist(),
        "hidden": hidden[i].tolist(), "pool1": first[i].flatten().tolist(),
        "pool2": second[i].flatten().tolist()} for i in range(len(labels))]})
    return manifest


def run(task, epochs, threads):
    torch.manual_seed(SEED)
    directory = ROOT / "artifacts/robust" / task
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / "best.pt"
    report_path = ROOT / "reports" / f"robust-{task}.json"
    if checkpoint.exists() or report_path.exists():
        raise SystemExit(f"Preserve existing experiment: {directory}")
    is_letter = task == "letters"
    baseline_path = ROOT / ("artifacts/letters/best.pt" if is_letter else "artifacts/best.pt")
    model = LetterCNN() if is_letter else DigitCNN()
    baseline_state = torch.load(baseline_path, map_location="cpu", weights_only=True)
    model.load_state_dict(baseline_state)
    if is_letter:
        from .emnist_data import load_partition as load_letters
        images, labels = load_letters(True)
        train, validation = letter_split(labels)
        prepared, blanks = prepare_images(images)
    else:
        images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
        train, validation = split_indices(labels)
        prepared, blanks = prepare_mnist(images), []
    np.savez(directory / "split.npz", train=train, validation=validation)
    x, y = torch.from_numpy(prepared), torch.from_numpy(labels.astype(np.int64))
    tx, ty, vx, vy = x[train], y[train], x[validation], y[validation]
    noisy = noisy_copy(vx, POLICY["validation_noise_seed"])
    baseline = {"clean": evaluate(model, vx, vy), "noisy": evaluate(model, noisy, vy)}
    metadata = {"task": task, "seed": SEED, "epochs_planned": epochs, "threads": threads,
        "preprocessing": VERSION, "policy": POLICY, "baseline_validation": baseline,
        "baseline_checkpoint_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        "split": {"train": len(tx), "validation": len(vx)}, "unreadable_train_indices": blanks,
        "optimizer": "AdamW", "learning_rate": .0003, "batch_size": 256, "history": []}
    write_json(report_path, metadata)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.0003, weight_decay=.0001)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, epochs, eta_min=.00002)
    best = float("inf")
    for epoch in range(epochs):
        start = time.perf_counter()
        model.train()
        order = torch.randperm(len(tx))
        for begin in range(0, len(tx), 256):
            indices = order[begin:begin + 256]
            batch = distort(tx[indices])
            # Include original examples so clean accuracy remains part of training.
            keep_clean = torch.rand(len(indices), 1, 1, 1) < .25
            batch = torch.where(keep_clean, tx[indices], batch)
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(model(batch), ty[indices])
            loss.backward()
            optimizer.step()
        clean, corrupted = evaluate(model, vx, vy), evaluate(model, noisy, vy)
        score = (clean["loss"] + corrupted["loss"]) / 2
        eligible = qualifies(baseline, clean, corrupted, POLICY["clean_accuracy_tolerance"][task])
        if eligible and score < best:
            best = score
            torch.save(model.state_dict(), checkpoint)
            metadata["selected_epoch"] = epoch + 1
            metadata["validation"] = {"clean": clean, "noisy": corrupted}
        metadata["history"].append({"epoch": epoch + 1, "clean": clean, "noisy": corrupted,
            "eligible": eligible, "seconds": time.perf_counter() - start})
        write_json(report_path, metadata)
        print(f"{task} {epoch+1}/{epochs}: clean {clean['accuracy']:.2%}, noisy {corrupted['accuracy']:.2%}, eligible={eligible}, {time.perf_counter()-start:.1f}s", flush=True)
        scheduler.step()
    if not checkpoint.exists():
        metadata["status"] = "No candidate passed validation; original retained"
        write_json(report_path, metadata)
        return
    # Selection is complete before either official test partition is loaded.
    if is_letter:
        test_images, test_labels = load_letters(False)
        test_prepared, _ = prepare_images(test_images)
    else:
        test_images, test_labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
        test_prepared = prepare_mnist(test_images)
    test_x, test_y = torch.from_numpy(test_prepared), torch.from_numpy(test_labels.astype(np.int64))
    test_noisy = noisy_copy(test_x, POLICY["test_noise_seed"])
    metadata["baseline_test"] = {"clean": evaluate(model_with_state(task, baseline_state), test_x, test_y),
        "noisy": evaluate(model_with_state(task, baseline_state), test_noisy, test_y)}
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    metadata["test"] = evaluate(model, test_x, test_y)
    metadata["noisy_test"] = evaluate(model, test_noisy, test_y)
    metadata["status"] = "Selected using validation only; official and synthetic test scores reported separately"
    class_labels = LABELS if is_letter else list("0123456789")
    indices = [int(torch.nonzero(test_y == i)[0]) for i in range(len(class_labels))]
    manifest = export(model, ROOT / "dist/model/robust" / task, metadata, test_x[indices], class_labels)
    metadata["model_sha256"] = manifest["sha256"]
    write_json(report_path, metadata)
    print(f"{task}: clean test {metadata['test']['accuracy']:.2%}; noisy test {metadata['noisy_test']['accuracy']:.2%}", flush=True)


def model_with_state(task, state):
    model = LetterCNN() if task == "letters" else DigitCNN()
    model.load_state_dict(state)
    return model.eval()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=["digits", "letters", "both"], default="both")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.epochs < 1 or args.threads < 1:
        parser.error("epochs and threads must be positive")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    for task in (["digits", "letters"] if args.task == "both" else [args.task]):
        run(task, args.epochs, args.threads)


if __name__ == "__main__":
    main()
