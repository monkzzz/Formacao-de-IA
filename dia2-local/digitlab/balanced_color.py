"""Frozen balanced color/legacy training and gated independent evaluation."""

import argparse
import copy
from datetime import datetime, timezone
import json
import math
import platform
import time

import numpy as np
from PIL import Image
import torch
from torch.nn import functional as F

from .balanced_color_data import make_raw
from .captcha_extension import baseline_model, balanced, digest
from .color_preprocess import prepare_color
from .color_study import gates as color_gates, metrics
from .confidence_broad import font_groups, update_average
from .data import load_partition, split_indices
from .model import augment
from .preprocess import prepare
from .train import ROOT, write_json

NAME = "balanced-color-training-v1"
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
SEED = 2026102401
POLICY = {"seed": SEED, "epochs": 4, "threads": 4, "batch_size": 128,
          "raw_train": 18000, "clean_train": 6000, "raw_development": 1800,
          "bridge_count": 2400, "clean_development": 5000,
          "learning_rate": .0001, "minimum_learning_rate": .00001,
          "weight_decay": .0001, "dropout": .15, "ema_decay": .99,
          "training_preprocessing": "RGB", "candidate_contracts": ["gray", "rgb"],
          "gates": {"accuracy_loss_tolerance": .001, "strict_90_gain": .005,
                    "brier_tolerance": .001, "ece_tolerance": .005,
                    "confident_error_increase": 0, "rejection_increase": 0},
          "selection": "Minimum development NLL among epoch/contract pairs passing against both baseline contracts",
          "official_inputs_for_training_or_selection": False, "desktop_p95_limit_ms": 150,
          "scope": "Synthetic development and subsequent gated tests; historical model/font/source exposure",
          "device": "cpu", "independent_human_review": "NOT RUN"}
SOURCES = ("balanced_color.py", "balanced_color_data.py", "captcha_extension.py",
           "color_study.py", "color_preprocess.py", "color_preprocess.js",
           "preprocessing_variants.py", "preprocess.py", "residual.py", "highres.py",
           "captcha.py", "ensemble_benchmark.py", "model.py", "confidence_broad.py",
           "confidence.py", "data.py", "train.py", "platform_support.py")


def verify(d):
    if d.get("visual_review_sha256") and digest(ROOT / "reports" / (NAME + "-visual-review.json")) != d["visual_review_sha256"]:
        raise ValueError("Visual review record changed")
    for name, value in d["frozen_sha256"].items():
        if digest(ROOT / name) != value:
            raise ValueError("Frozen source/asset changed: " + name)
    for name, value in d.get("cache_sha256", {}).items():
        if digest(DIRECTORY / name) != value:
            raise ValueError("Frozen cache/evidence changed: " + name)


def cache(name, data, d):
    np.savez(DIRECTORY / (name + ".npz"), **data)
    d["cache_sha256"][name + ".npz"] = digest(DIRECTORY / (name + ".npz"))


def read(name):
    with np.load(DIRECTORY / (name + ".npz"), allow_pickle=False) as f:
        return {k: f[k] for k in f.files}


def clean_set(images, labels, indices):
    rgba = [np.asarray(Image.fromarray(images[i]).convert("RGBA")) for i in indices]
    return {"gray": np.stack([prepare(p, 64) for p in rgba]),
            "rgb": np.stack([prepare_color(p) for p in rgba]),
            "y": labels[indices].astype(np.int64), "gray_rejected": np.zeros(len(indices), bool)}


def prepare_data():
    if DIRECTORY.exists() or REPORT.exists():
        raise FileExistsError("Preserve completed experiment")
    DIRECTORY.mkdir(parents=True)
    fonts = font_groups(ROOT / "data/open-fonts")
    paths = [ROOT / "digitlab" / n for n in SOURCES]
    paths += [ROOT / "docs/balanced-color-training.md", ROOT / "artifacts/captcha-v3/best.pt", ROOT / "artifacts/frozen-app.zip"]
    paths += [p for p in (ROOT / "dist").rglob("*") if p.is_file() and p.suffix in (".js", ".html", ".css", ".bin", ".json")]
    paths += [p for group in fonts.values() for p in group]
    paths += [ROOT.parent / "Dia2/Dataset-MNIST/data" / n for n in ("train-images-idx3-ubyte.gz", "train-labels-idx1-ubyte.gz")]
    d = {"status": "PREPARING", "policy": POLICY, "history": [], "cache_sha256": {},
         "started_utc": datetime.now(timezone.utc).isoformat(),
         "frozen_sha256": {str(p.relative_to(ROOT, walk_up=True)): digest(p) for p in paths},
         "environment": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__, "device": "cpu"}}
    write_json(REPORT, d)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    train, validation = split_indices(labels)
    validation_hashes = {digest_image(images[i]) for i in validation}
    train = np.array([i for i in train if digest_image(images[i]) not in validation_hashes])
    d["source_counts"] = {"train": len(train), "development": len(validation)}
    np.savez(DIRECTORY / "source-split.npz", train=train, validation=validation)
    d["cache_sha256"]["source-split.npz"] = digest(DIRECTORY / "source-split.npz")
    print("Preparing balanced raw training and independent development images...", flush=True)
    data, records = make_raw(images, labels, train, fonts["train"], 18000, SEED, DIRECTORY / "train-fixtures")
    cache("train-raw", {"rgb": data["rgb"], "y": data["y"]}, d)
    write_json(DIRECTORY / "train-records.json", records)
    del data
    chosen = balanced(labels, train, 6000, SEED + 1)
    data = clean_set(images, labels, chosen)
    cache("train-clean", {"rgb": data["rgb"], "y": data["y"], "source_indices": chosen}, d)
    del data
    for name, count, seed, kinds in (("raw", 1800, SEED + 2, None), ("bridge", 2400, SEED + 3, ("legacy",))):
        kwargs = {} if kinds is None else {"kinds": kinds}
        data, records = make_raw(images, labels, validation, fonts["development"], count, seed, DIRECTORY / (name + "-fixtures"), **kwargs)
        cache(name, data, d)
        write_json(DIRECTORY / (name + "-records.json"), records)
        del data
    cache("clean", clean_set(images, labels, validation), d)
    for p in DIRECTORY.glob("*-records.json"):
        d["cache_sha256"][p.name] = digest(p)
    model = baseline_model()
    d["baseline_development"] = {contract: evaluate(model, contract, score_path=DIRECTORY / ("baseline-" + contract + "-scores.npz")) for contract in ("gray", "rgb")}
    for contract, result in d["baseline_development"].items():
        name = "baseline-" + contract + "-scores.npz"
        d["cache_sha256"][name] = digest(DIRECTORY / name)
        print(f"Baseline {contract}: raw={result['raw']['accuracy']:.3%}, correct >90={result['raw']['correct_above_90_fraction']:.3%}, wrong >90={result['raw']['wrong_above_90_count']}, bridge={result['bridge']['accuracy']:.3%}", flush=True)
    d["status"] = "PREPARED; visual review required before training"
    verify(d)
    write_json(REPORT, d)
    print(d["status"], flush=True)


def digest_image(image):
    import hashlib
    return hashlib.sha256(image.tobytes()).digest()


def measure(model, data, contract):
    model.eval()
    with torch.no_grad():
        scores = torch.cat([model(torch.from_numpy(b)).softmax(1) for b in np.array_split(data[contract], math.ceil(len(data["y"]) / 256))]).numpy()
    failed = data["gray_rejected"] if contract == "gray" else np.zeros(len(data["y"]), bool)
    scores[failed] = .1
    return metrics(scores, data["y"], failed), scores, failed


def evaluate(model, contract, prefix="", score_path=None):
    results, vectors = {}, {}
    for group in ("raw", "bridge", "clean"):
        data = read(prefix + group)
        results[group], scores, failed = measure(model, data, contract)
        vectors[group], vectors[group + "_labels"], vectors[group + "_rejected"] = scores, data["y"], failed
        if group == "raw":
            records = json.loads((DIRECTORY / (prefix + "raw-records.json")).read_text())
            for kind in ("legacy", "color", "isoluminant"):
                mask = np.array([r["kind"] == kind for r in records])
                results[kind] = metrics(scores[mask], data["y"][mask], failed[mask])
    if score_path:
        np.savez_compressed(score_path, **vectors)
    return results


def gates(candidate, baseline):
    checks = color_gates(candidate, baseline)
    checks["bridge_accuracy"] = candidate["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - .001
    checks["bridge_rejections"] = candidate["bridge"]["rejected"] <= baseline["bridge"]["rejected"]
    return checks


def train():
    d = json.loads(REPORT.read_text())
    verify(d)
    if d["history"] or (DIRECTORY / "selection.json").exists():
        raise ValueError("Preserve completed or partial training")
    visual_path = ROOT / "reports" / (NAME + "-visual-review.json")
    visual = json.loads(visual_path.read_text())
    if visual["status"] != "INSPECTED" or not visual["allow_training"]:
        raise ValueError("Review the fixed training sample before training")
    d["visual_review_sha256"] = digest(visual_path)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    network = baseline_model()
    network.dropout.p = .15
    average = copy.deepcopy(network).eval()
    optimizer = torch.optim.AdamW(network.parameters(), lr=.0001, weight_decay=.0001)
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 4, eta_min=.00001)
    raw, clean = read("train-raw"), read("train-clean")
    inputs = torch.from_numpy(np.concatenate([raw["rgb"], clean["rgb"]]))
    targets = torch.from_numpy(np.concatenate([raw["y"], clean["y"]]))
    del raw, clean
    best = float("inf")
    d["status"] = "TRAINING"
    for epoch in range(1, 5):
        start = time.perf_counter()
        network.train()
        order = torch.randperm(len(targets))
        for batch in order.split(128):
            optimizer.zero_grad(set_to_none=True)
            loss = F.cross_entropy(network(augment(inputs[batch])), targets[batch])
            loss.backward()
            optimizer.step()
            update_average(average, network, .99)
        row = {"epoch": epoch, "contracts": {}}
        for contract in ("gray", "rgb"):
            path = DIRECTORY / f"epoch-{epoch}-{contract}-scores.npz"
            result = evaluate(average, contract, score_path=path)
            checks = {ref: gates(result, baseline) for ref, baseline in d["baseline_development"].items()}
            passes = all(all(c.values()) for c in checks.values())
            row["contracts"][contract] = {"metrics": result, "gates": checks, "eligible": passes, "scores_sha256": digest(path)}
            d["cache_sha256"][path.name] = digest(path)
            if passes and result["raw"]["loss"] < best:
                best = result["raw"]["loss"]
                torch.save(average.state_dict(), DIRECTORY / "best.pt")
                d["selected_epoch"], d["selected_contract"] = epoch, contract
            print(f"Epoch {epoch} {contract}: raw={result['raw']['accuracy']:.3%}, correct >90={result['raw']['correct_above_90_fraction']:.3%}, wrong >90={result['raw']['wrong_above_90_count']}, bridge={result['bridge']['accuracy']:.3%}, clean={result['clean']['accuracy']:.3%}, eligible={passes}", flush=True)
        row["seconds"] = time.perf_counter() - start
        d["history"].append(row)
        torch.save(average.state_dict(), DIRECTORY / "last.pt")
        verify(d)
        write_json(REPORT, d)
        schedule.step()
    with (DIRECTORY / "development-report.json").open("x") as stream:
        json.dump(d, stream, indent=2)
    selection = {"epoch": d.get("selected_epoch"), "contract": d.get("selected_contract"),
                 "checkpoint_sha256": digest(DIRECTORY / "best.pt") if d.get("selected_epoch") else None,
                 "development_sha256": digest(DIRECTORY / "development-report.json"), "reserved_data_used": False}
    with (DIRECTORY / "selection.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    d["status"] = "SELECTED; browser/test/official NOT RUN" if selection["epoch"] else "RETAIN BASELINE; no development-eligible pair"
    d["completed_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(REPORT, d)
    print(d["status"], flush=True)


def selected():
    d = json.loads(REPORT.read_text())
    verify(d)
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    if not selection["epoch"]:
        raise ValueError("No eligible development pair; reserved and official inputs remain unopened")
    if digest(DIRECTORY / "best.pt") != selection["checkpoint_sha256"] or digest(DIRECTORY / "development-report.json") != selection["development_sha256"]:
        raise ValueError("Frozen selection changed")
    return d, selection


def test():
    d, selection = selected()
    browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    if browser["status"] != "PASS" or browser["checkpoint_sha256"] != selection["checkpoint_sha256"] or browser["p95_ms"] >= 150:
        raise ValueError("Require matched browser parity before reserved data")
    marker = DIRECTORY / "test-started.json"
    with marker.open("x") as stream:
        json.dump(selection, stream)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    source_images, _ = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    source_hashes = {digest_image(i) for i in source_images}
    overlap = sum(digest_image(i) in source_hashes for i in images)
    if overlap:
        d.update(status="FAIL: reserved source overlap", test_overlap=overlap)
        write_json(REPORT, d)
        raise ValueError("Reserved source integrity failed")
    fonts = font_groups(ROOT / "data/open-fonts")["test"]
    for name, count, seed, kinds in (("raw", 1800, SEED + 20, None), ("bridge", 2400, SEED + 21, ("legacy",))):
        kwargs = {} if kinds is None else {"kinds": kinds}
        data, records = make_raw(images, labels, np.arange(len(labels)), fonts, count, seed, **kwargs)
        cache("test-" + name, data, d)
        write_json(DIRECTORY / ("test-" + name + "-records.json"), records)
    cache("test-clean", clean_set(images, labels, np.arange(len(labels))), d)
    candidate = baseline_model()
    candidate.load_state_dict(torch.load(DIRECTORY / "best.pt", map_location="cpu", weights_only=True))
    result = evaluate(candidate, selection["contract"], "test-", DIRECTORY / "test-candidate-scores.npz")
    baselines = {contract: evaluate(baseline_model(), contract, "test-", DIRECTORY / ("test-baseline-" + contract + "-scores.npz")) for contract in ("gray", "rgb")}
    checks = {contract: gates(result, baseline) for contract,baseline in baselines.items()}
    d.update(test={"candidate": result, "baselines": baselines, "gates": checks},
             independent_test_eligible=all(all(c.values()) for c in checks.values()), test_overlap=0)
    d["status"] = "PASS: independent gates; official NOT RUN" if d["independent_test_eligible"] else "RETAIN BASELINE: independent gate failed"
    verify(d)
    write_json(REPORT, d)
    print(d["status"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "train", "test"), required=True)
    args = parser.parse_args()
    torch.set_num_threads(4)
    {"prepare": prepare_data, "train": train, "test": test}[args.stage]()
