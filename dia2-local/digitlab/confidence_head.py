"""Independent final-layer fine-tuning; no challenge data or score rescaling."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import numpy as np
import torch
from torch.nn import functional as F

from .captcha import TRAIN_FONTS
from .confidence import DEV_FONTS, TEST_FONTS, POLICY as GATE_POLICY, digest, eligible, measure
from .data import load_partition, split_indices
from .highres import EXTRA_FONTS
from .preprocess import prepare_mnist
from .residual import ADDED_FONTS, ResidualCNN, make_raw
from .train import ROOT, write_json

NAME = "captcha-confidence-head-v1"
SEED = 2026101702
POLICY = {"seed": SEED, "epochs": 16, "raw_training": 40000, "clean_training": 20000,
          "batch_size": 512, "learning_rate": .0002, "weight_decay": .001,
          "objective": "Unmodified supervised cross entropy; only fc2 weights and bias train; all image features frozen",
          "gates": GATE_POLICY["gates"], "selection": "Lowest development NLL among eligible epochs",
          "temperature": 1.0, "official_inputs_used": False,
          "development": "Same fixed independent development set as full-network experiment; legitimate shared model-selection set",
          "test": "Distinct seed, held-out fonts, opened only after final selection"}


def features(model, x):
    model.eval()
    with torch.no_grad():
        return torch.cat([model.features(x[i:i + 256])[2] for i in range(0, len(x), 256)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["train", "test"], required=True)
    args = parser.parse_args()
    directory = ROOT / "artifacts" / NAME
    output = ROOT / "reports" / (NAME + ".json")
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    baseline = ResidualCNN()
    baseline_path = ROOT / "artifacts/captcha-v3/best.pt"
    baseline.load_state_dict(torch.load(baseline_path, map_location="cpu", weights_only=True))
    model = ResidualCNN()
    model.load_state_dict(baseline.state_dict())
    if args.stage == "train":
        if directory.exists() or output.exists():
            raise SystemExit("Preserve previous run")
        directory.mkdir(parents=True)
        metadata = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "TRAINING",
                    "policy": POLICY, "history": [], "baseline_checkpoint_sha256": digest(baseline_path),
                    "source_sha256": digest(Path(__file__)), "shared_gate_source_sha256": digest(ROOT / "digitlab/confidence.py")}
        write_json(output, metadata)
        images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
        train, validation = split_indices(labels)
        clean = torch.from_numpy(prepare_mnist(images, 64))
        targets = torch.from_numpy(labels.astype(np.int64))
        font_root = Path("C:/Windows/Fonts")
        train_fonts = [font_root / name for name in TRAIN_FONTS + EXTRA_FONTS + ADDED_FONTS]
        dev_fonts = [font_root / name for name in DEV_FONTS]
        metadata["font_sha256"] = {p.name: digest(p) for p in train_fonts + dev_fonts}
        print("Preparing independent classifier-training and shared development inputs...", flush=True)
        rx, ry = make_raw(images, labels, validation, dev_fonts, 6000, GATE_POLICY["seed"] + 1)
        base = {"raw": measure(baseline, rx, ry)[0], "clean": measure(baseline, clean[validation], targets[validation])[0]}
        metadata["baseline_validation"] = base
        tx, ty = make_raw(images, labels, train, train_fonts, POLICY["raw_training"], SEED + 100)
        chosen = train[torch.randperm(len(train))[:POLICY["clean_training"]].numpy()]
        tx, ty = torch.cat([tx, clean[chosen]]), torch.cat([ty, targets[chosen]])
        print("Extracting frozen image features...", flush=True)
        fx = features(model, tx)
        del tx
        optimizer = torch.optim.AdamW(model.fc2.parameters(), lr=POLICY["learning_rate"], weight_decay=POLICY["weight_decay"])
        best = float("inf")
        for epoch in range(POLICY["epochs"]):
            start = time.perf_counter()
            order = torch.randperm(len(fx))
            for begin in range(0, len(fx), POLICY["batch_size"]):
                ids = order[begin:begin + POLICY["batch_size"]]
                optimizer.zero_grad(set_to_none=True)
                F.cross_entropy(model.fc2(fx[ids]), ty[ids]).backward()
                optimizer.step()
            metrics = {"raw": measure(model, rx, ry)[0], "clean": measure(model, clean[validation], targets[validation])[0]}
            passes = eligible(metrics, base)
            if passes and metrics["raw"]["loss"] < best:
                best = metrics["raw"]["loss"]
                torch.save(model.state_dict(), directory / "best.pt")
                metadata.update(selected_epoch=epoch + 1, validation=metrics)
            metadata["history"].append({"epoch": epoch + 1, **metrics, "eligible": passes, "seconds": time.perf_counter() - start})
            write_json(output, metadata)
            print(f"Head epoch {epoch+1}/{POLICY['epochs']}: clean={metrics['clean']['accuracy']:.3%}, raw={metrics['raw']['accuracy']:.3%}, correct >=90={metrics['raw']['correct_at_90_fraction']:.3%}, NLL={metrics['raw']['loss']:.5f}, eligible={passes}", flush=True)
        # Verify frozen feature extractor and only trained final-layer changes.
        assert all(torch.equal(value, baseline.state_dict()[key]) for key, value in model.state_dict().items() if not key.startswith("fc2."))
        torch.save(model.state_dict(), directory / "last.pt")
        metadata["status"] = "SELECTED; fresh test NOT RUN" if "selected_epoch" in metadata else "RETAIN BASELINE; no eligible epoch"
        write_json(directory / "selection.json", {"selected_epoch": metadata.get("selected_epoch"), "policy": POLICY,
                   "test_loaded": False, "checkpoint_sha256": digest(directory / "best.pt") if "selected_epoch" in metadata else None})
        write_json(output, metadata)
        return
    metadata = json.loads(output.read_text())
    selection = json.loads((directory / "selection.json").read_text())
    assert selection["selected_epoch"] and "test" not in metadata
    assert digest(directory / "best.pt") == selection["checkpoint_sha256"]
    assert digest(Path(__file__)) == metadata["source_sha256"]
    with (directory / "test-started.json").open("x") as stream:
        json.dump(selection, stream)
    model.load_state_dict(torch.load(directory / "best.pt", map_location="cpu", weights_only=True))
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    clean = torch.from_numpy(prepare_mnist(images, 64))
    target = torch.from_numpy(labels.astype(np.int64))
    raw, raw_y = make_raw(images, labels, np.arange(len(labels)), [Path("C:/Windows/Fonts") / n for n in TEST_FONTS],
                         10000, SEED + 2, directory / "fixtures")
    results, predictions = {}, {}
    for name, network in [("baseline", baseline), ("candidate", model)]:
        results[name] = {}
        for kind, x, y in [("clean", clean, target), ("raw", raw, raw_y)]:
            results[name][kind], predictions[name + "_" + kind] = measure(network, x, y)
    np.savez_compressed(directory / "test-predictions.npz", **predictions, labels=raw_y.numpy())
    metadata["test"] = results
    metadata["independent_test_eligible"] = eligible(results["candidate"], results["baseline"])
    metadata["status"] = "PASS: independent gates; browser/challenge NOT RUN" if metadata["independent_test_eligible"] else "RETAIN BASELINE: independent test gate failed"
    write_json(output, metadata)
    print(json.dumps({"status": metadata["status"], "test": results}, indent=2))


if __name__ == "__main__":
    main()
