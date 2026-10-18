"""Bounded separate 64px training extension, with frozen independent gates."""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import platform
from pathlib import Path
import time

import numpy as np
from PIL import Image
import torch
from torch.nn import functional as F

from . import supplementary_data as extra
from .captcha_extension_data import make_set
from .confidence import score_metrics
from .confidence_broad import font_groups, update_average
from .data import load_partition, split_indices
from .model import augment
from .preprocess import prepare_mnist
from .residual import ResidualCNN, make_raw
from .train import ROOT, write_json

NAME = "captcha-training-extension-v1"
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
SEED = 2026102201
POLICY = {"seed": SEED, "epochs": 4, "threads": 4, "batch_size": 128,
          "raw_train_count": 32400, "mnist_clean_train_count": 10800, "emnist_clean_train_count": 5400,
          "development_count": 5400, "test_count": 5400, "bridge_count": 2400,
          "learning_rate": .00015, "minimum_learning_rate": .00001, "weight_decay": .0001,
          "training_dropout": .15, "ema_decay": .99,
          "objective": "Unmodified cross entropy; no score scaling",
          "preprocessing": "Unchanged production 64px contract; training-only study",
          "selection": "Minimum raw development NLL among eligible EMA epochs; otherwise preserve baseline",
          "gates": {"raw_accuracy_tolerance": .001, "clean_accuracy_tolerance": .001,
                    "bridge_accuracy_tolerance": .001, "minimum_strict_90_coverage_gain": .005,
                    "brier_tolerance": .001, "ece_tolerance": .005, "confident_error_increase": 0},
          "desktop_p95_limit_ms": 150, "official_inputs_for_training_or_selection": False,
          "independent_human_readability_review": "NOT RUN; source labels and automated geometry/gap checks only",
          "scope": "Synthetic CAPTCHA-style extension, not collected real CAPTCHA population accuracy",
          "prior_exposure": "Historical model/fonts/MNIST/EMNIST exposure; new synthetic seeds and current source splits"}
SOURCES = ("captcha_extension.py", "captcha_extension_data.py", "supplementary_data.py", "emnist_data.py",
           "confidence.py", "confidence_broad.py", "residual.py", "highres.py", "captcha.py", "ensemble_benchmark.py",
           "data.py", "preprocess.py", "model.py", "platform_support.py", "train.py")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(scores, labels):
    result = score_metrics(scores, labels)
    correct, high = scores.argmax(1) == labels, scores.max(1) > .9
    result.update(correct_above_90_count=int((correct & high).sum()),
                  correct_above_90_fraction=float((correct & high).mean()),
                  wrong_above_90_count=int((~correct & high).sum()))
    return result


def measure(model, inputs, labels):
    model.eval()
    with torch.no_grad():
        scores = torch.cat([model(inputs[i:i+256]).softmax(1) for i in range(0, len(inputs), 256)]).numpy()
    return metrics(scores, labels.numpy()), scores


def per_group(scores, labels, records):
    groups = {}
    for field in ("source", "condition", "severity"):
        values = np.array([str(r[field]) for r in records])
        groups[field] = {value: metrics(scores[values == value], labels[values == value]) for value in np.unique(values)}
    return groups


def eligible(candidate, baseline):
    gates = POLICY["gates"]
    raw, old = candidate["raw"], baseline["raw"]
    return (raw["count"] == old["count"]
            and raw["accuracy"] >= old["accuracy"] - gates["raw_accuracy_tolerance"]
            and all(candidate[k]["accuracy"] >= baseline[k]["accuracy"] - gates["clean_accuracy_tolerance"] for k in ("mnist", "emnist"))
            and candidate["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - gates["bridge_accuracy_tolerance"]
            and raw["correct_above_90_count"] - old["correct_above_90_count"] >= math.ceil(gates["minimum_strict_90_coverage_gain"] * raw["count"])
            and raw["loss"] < old["loss"]
            and raw["brier"] <= old["brier"] + gates["brier_tolerance"]
            and raw["ece_10_bins"] <= old["ece_10_bins"] + gates["ece_tolerance"]
            and raw["wrong_above_90_count"] <= old["wrong_above_90_count"])


def baseline_model():
    model = ResidualCNN()
    model.load_state_dict(torch.load(ROOT / "artifacts/captcha-v3/best.pt", map_location="cpu", weights_only=True))
    blob = b"".join(t.numpy().astype("<f4").tobytes() for t in model.state_dict().values())
    manifest = json.loads((ROOT / "dist/model/captcha-v3/digits/manifest.json").read_text())
    if hashlib.sha256(blob).hexdigest() != manifest["sha256"]:
        raise ValueError("Baseline checkpoint/browser export mismatch")
    return model


def verify(metadata):
    for name, checksum in metadata["source_sha256"].items():
        if digest(ROOT / "digitlab" / name) != checksum:
            raise ValueError("Frozen training source changed: " + name)
    for name, checksum in metadata["preserved_sha256"].items():
        if digest(ROOT / name) != checksum:
            raise ValueError("Preserved model/app changed: " + name)
    if digest(ROOT / "docs/captcha-training-extension.md") != metadata["protocol_sha256"]:
        raise ValueError("Predeclared training protocol changed")
    for name, checksum in metadata["fonts_sha256"].items():
        if digest(ROOT / name) != checksum:
            raise ValueError("Font identity changed")
    for name, checksum in metadata["caches_sha256"].items():
        if digest(DIRECTORY / name) != checksum:
            raise ValueError("Cached training/development identity changed")
    for name, checksum in metadata.get("epoch_scores_sha256", {}).items():
        if digest(DIRECTORY / name) != checksum:
            raise ValueError("Recorded epoch scores changed")


def balanced(labels, indices, count, seed):
    if count % 10:
        raise ValueError("Balanced clean count must be a multiple of ten")
    rng = np.random.default_rng(seed)
    return rng.permutation(np.concatenate([rng.choice(indices[labels[indices] == digit], count // 10, replace=False) for digit in range(10)]))


def save_cache(name, x, y):
    destination = DIRECTORY / (name + ".npz")
    np.savez(destination, x=x, y=y)
    return destination.name, digest(destination)


def read_cache(name):
    with np.load(DIRECTORY / (name + ".npz"), allow_pickle=False) as cached:
        return torch.from_numpy(cached["x"]), torch.from_numpy(cached["y"].astype(np.int64))


def prepare():
    if DIRECTORY.exists() or REPORT.exists():
        raise FileExistsError("Preserve existing extension")
    DIRECTORY.mkdir(parents=True)
    fonts = font_groups(ROOT / "data/open-fonts")
    preserved = [*ROOT.glob("dist/v3/*.js"), ROOT / "dist/index.html", ROOT / "artifacts/frozen-app.zip",
                 ROOT / "artifacts/captcha-v3/best.pt"]
    for folder in (ROOT / "dist/model", ROOT / "dist/model/captcha-v3/digits", ROOT / "dist/model/mnist-supplementary-v1/digits"):
        preserved.extend([folder / "weights.bin", folder / "manifest.json"])
    metadata = {"status": "PREPARING", "started_utc": datetime.now(timezone.utc).isoformat(), "policy": POLICY,
        "source_sha256": {n: digest(ROOT / "digitlab" / n) for n in SOURCES},
        "protocol_sha256": digest(ROOT / "docs/captcha-training-extension.md"),
        "preserved_sha256": {str(p.relative_to(ROOT)): digest(p) for p in preserved},
        "fonts_sha256": {str(p.relative_to(ROOT)): digest(p) for group in fonts.values() for p in group},
        "caches_sha256": {}, "history": [],
        "environment": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__, "platform": platform.platform(),
                        "device": "cpu", "cuda_available": torch.cuda.is_available()}}
    write_json(REPORT, metadata)
    mnist, ml = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    emnist, el = extra.load_partition(True)
    mt, mv = split_indices(ml)
    mt = mt[extra.unique_indices(mnist[mt], extra.fingerprints(mnist[mv]))]
    independent = extra.unique_indices(emnist, extra.fingerprints(mnist))
    et, ev = extra.stratified_split(el, independent, seed=SEED)
    clean_m = balanced(ml, mt, POLICY["mnist_clean_train_count"], SEED + 1)
    clean_e = balanced(el, et, POLICY["emnist_clean_train_count"], SEED + 2)
    np.savez(DIRECTORY / "split.npz", mnist_train=mt, mnist_validation=mv, emnist_train=et, emnist_validation=ev,
             clean_mnist_train=clean_m, clean_emnist_train=clean_e)
    metadata["caches_sha256"]["split.npz"] = digest(DIRECTORY / "split.npz")
    metadata["source_counts"] = {"mnist_train": len(mt), "mnist_validation": len(mv), "emnist_train": len(et), "emnist_validation": len(ev)}
    for name, mi, ei, font_group, count, seed in (
            ("train", mt, et, "train", POLICY["raw_train_count"], SEED + 10),
            ("raw", mv, ev, "development", POLICY["development_count"], SEED + 11)):
        print(f"Generating {name}: {count:,} balanced independently rendered images...", flush=True)
        x, y, records = make_set(mnist, ml, mi, emnist, el, ei, fonts[font_group], count, seed, DIRECTORY / (name + "-fixtures"))
        for row in records:
            row["font"] = str(Path(row["font"]).relative_to(ROOT))
        write_json(DIRECTORY / (name + "-records.json"), records)
        metadata["caches_sha256"][name + "-records.json"] = digest(DIRECTORY / (name + "-records.json"))
        if name == "train":
            x = np.concatenate((x, prepare_mnist(mnist[clean_m], 64), prepare_mnist(emnist[clean_e], 64)))
            y = np.concatenate((y, ml[clean_m].astype(np.int64), el[clean_e].astype(np.int64)))
        key, checksum = save_cache(name, x, y)
        metadata["caches_sha256"][key] = checksum
        del x, y, records
        write_json(REPORT, metadata)
    for name, images, labels, indices in (("mnist", mnist, ml, mv), ("emnist", emnist, el, ev)):
        key, checksum = save_cache(name, prepare_mnist(images[indices], 64), labels[indices])
        metadata["caches_sha256"][key] = checksum
    print("Generating independent legacy bridge...", flush=True)
    bx, by = make_raw(mnist, ml, mv, fonts["development"], POLICY["bridge_count"], SEED + 12)
    key, checksum = save_cache("bridge", bx.numpy(), by.numpy())
    metadata["caches_sha256"][key] = checksum
    metadata["dataset_sha256"] = {str(p.relative_to(ROOT.parent)): digest(p) for p in
        [*(ROOT.parent / "Dia2/Dataset-MNIST/data").glob("*ubyte.gz"), *(ROOT / "data/emnist-digits").glob("*ubyte.gz")]}
    baseline = baseline_model()
    metadata["baseline_validation"] = {}
    baseline_vectors = {}
    raw_records = json.loads((DIRECTORY / "raw-records.json").read_text())
    for name in ("raw", "mnist", "emnist", "bridge"):
        inputs, targets = read_cache(name)
        metadata["baseline_validation"][name], baseline_vectors[name] = measure(baseline, inputs, targets)
        if name == "raw":
            metadata["baseline_per_group"] = per_group(baseline_vectors[name], targets.numpy(), raw_records)
    np.savez_compressed(DIRECTORY / "baseline-validation-scores.npz", **baseline_vectors)
    metadata["caches_sha256"]["baseline-validation-scores.npz"] = digest(DIRECTORY / "baseline-validation-scores.npz")
    metadata["status"] = "PREPARED; training/reserved/browser/official NOT RUN"
    verify(metadata)
    write_json(REPORT, metadata)
    print("Baseline:", json.dumps({k: {a: v[a] for a in ("accuracy", "correct_above_90_fraction", "loss")} for k,v in metadata["baseline_validation"].items()}), flush=True)


def train():
    metadata = json.loads(REPORT.read_text())
    if metadata["history"] or (DIRECTORY / "selection.json").exists():
        raise FileExistsError("Preserve existing training history")
    verify(metadata)
    model = baseline_model()
    model.dropout.p = POLICY["training_dropout"]
    average = copy.deepcopy(model)
    optimizer = torch.optim.AdamW(model.parameters(), lr=POLICY["learning_rate"], weight_decay=POLICY["weight_decay"])
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, POLICY["epochs"], eta_min=POLICY["minimum_learning_rate"])
    tx, ty = read_cache("train")
    validation = {name: read_cache(name) for name in ("raw", "mnist", "emnist", "bridge")}
    raw_records = json.loads((DIRECTORY / "raw-records.json").read_text())
    metadata["epoch_scores_sha256"] = {}
    metadata["status"] = "TRAINING"
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
            update_average(average, model, POLICY["ema_decay"])
        result, vectors = {}, {}
        for name,data in validation.items():
            result[name], vectors[name] = measure(average, *data)
        score_file = f"epoch-{epoch+1}-validation-scores.npz"
        np.savez_compressed(DIRECTORY / score_file, **vectors)
        metadata["epoch_scores_sha256"][score_file] = digest(DIRECTORY / score_file)
        passes = eligible(result, metadata["baseline_validation"])
        if passes and result["raw"]["loss"] < best:
            best = result["raw"]["loss"]
            torch.save(average.state_dict(), DIRECTORY / "best.pt")
            metadata.update(selected_epoch=epoch + 1, validation=result)
        metadata["history"].append({"epoch": epoch + 1, "validation": result, "eligible": passes,
                                    "raw_per_group": per_group(vectors["raw"], validation["raw"][1].numpy(), raw_records),
                                    "seconds": time.perf_counter() - start})
        torch.save(average.state_dict(), DIRECTORY / "last.pt")
        write_json(REPORT, metadata)
        print(f"Epoch {epoch+1}: raw={result['raw']['accuracy']:.3%}, correct >90={result['raw']['correct_above_90_fraction']:.3%}, NLL={result['raw']['loss']:.5f}, MNIST={result['mnist']['accuracy']:.3%}, EMNIST={result['emnist']['accuracy']:.3%}, bridge={result['bridge']['accuracy']:.3%}, eligible={passes}, {time.perf_counter()-start:.1f}s", flush=True)
        schedule.step()
    verify(metadata)
    frozen_report = DIRECTORY / "development-report.json"
    with frozen_report.open("x") as stream:
        json.dump(metadata, stream, indent=2)
    selection = {"selected_epoch": metadata.get("selected_epoch"), "checkpoint_sha256": digest(DIRECTORY / "best.pt") if "selected_epoch" in metadata else None,
                 "development_report_sha256": digest(frozen_report), "source_sha256": metadata["source_sha256"], "policy": POLICY, "reserved_test_loaded": False}
    with (DIRECTORY / "selection.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    metadata.update(status="SELECTED; browser/reserved/official NOT RUN" if selection["selected_epoch"] else "RETAIN BASELINE; no eligible epoch",
                    completed_utc=datetime.now(timezone.utc).isoformat())
    write_json(REPORT, metadata)
    print(metadata["status"], flush=True)


def selected():
    metadata = json.loads(REPORT.read_text())
    verify(metadata)
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    if not selection["selected_epoch"]:
        raise ValueError("No eligible development selection; reserved data remain unopened")
    if (digest(DIRECTORY / "development-report.json") != selection["development_report_sha256"]
            or digest(DIRECTORY / "best.pt") != selection["checkpoint_sha256"]):
        raise ValueError("Frozen selection changed")
    return metadata, selection


def final_test():
    metadata, selection = selected()
    if "test" in metadata or (DIRECTORY / "test-started.json").exists():
        raise ValueError("Preserve completed reserved evaluation")
    browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    if browser["status"] != "PASS" or browser["checkpoint_sha256"] != selection["checkpoint_sha256"] or browser["p95_ms"] >= POLICY["desktop_p95_limit_ms"]:
        raise ValueError("Require matched browser parity and desktop speed before reserved data")
    with (DIRECTORY / "test-started.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    mi, ml = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    ei, el = extra.load_partition(False)
    m_train, _ = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    e_train, _ = extra.load_partition(True)
    train_hashes = set(extra.fingerprints(m_train)) | set(extra.fingerprints(e_train))
    overlap = {"mnist": sum(h in train_hashes for h in extra.fingerprints(mi)), "emnist": sum(h in train_hashes for h in extra.fingerprints(ei))}
    if any(overlap.values()):
        metadata.update(status="FAIL: exact reserved/source pixel overlap; no test metrics", reserved_overlap=overlap)
        write_json(REPORT, metadata)
        raise ValueError("Reserved source integrity failed")
    fonts = font_groups(ROOT / "data/open-fonts")["test"]
    rx, ry, records = make_set(mi, ml, np.arange(len(ml)), ei, el, np.arange(len(el)), fonts, POLICY["test_count"], SEED + 20, DIRECTORY / "test-fixtures")
    write_json(DIRECTORY / "test-records.json", records)
    bx, by = make_raw(mi, ml, np.arange(len(ml)), fonts, POLICY["bridge_count"], SEED + 21)
    data = {"raw": (torch.from_numpy(rx), torch.from_numpy(ry)),
            "mnist": (torch.from_numpy(prepare_mnist(mi, 64)), torch.from_numpy(ml.astype(np.int64))),
            "emnist": (torch.from_numpy(prepare_mnist(ei, 64)), torch.from_numpy(el.astype(np.int64))), "bridge": (bx, by)}
    candidate = baseline_model()
    candidate.load_state_dict(torch.load(DIRECTORY / "best.pt", map_location="cpu", weights_only=True))
    results, vectors = {}, {}
    for name, network in (("baseline", baseline_model()), ("candidate", candidate)):
        results[name] = {}
        for group, sample in data.items():
            results[name][group], vectors[name + "_" + group] = measure(network, *sample)
            vectors[group + "_labels"] = sample[1].numpy()
    np.savez_compressed(DIRECTORY / "reserved-scores.npz", **vectors)
    metadata.update(test=results, independent_test_eligible=eligible(results["candidate"], results["baseline"]), reserved_overlap=overlap,
                    reserved_scores_sha256=digest(DIRECTORY / "reserved-scores.npz"))
    metadata["test_per_group"] = {name: per_group(vectors[name + "_raw"], ry, records) for name in results}
    base_correct = vectors["baseline_raw"].argmax(1) == ry
    candidate_correct = vectors["candidate_raw"].argmax(1) == ry
    metadata["paired_raw_test"] = {"candidate_only_correct": int((candidate_correct & ~base_correct).sum()),
                                   "baseline_only_correct": int((base_correct & ~candidate_correct).sum())}
    metadata["status"] = "PASS: independent gates; official NOT RUN" if metadata["independent_test_eligible"] else "RETAIN BASELINE: independent gate failed"
    verify(metadata)
    write_json(REPORT, metadata)
    print(metadata["status"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "train", "test"), required=True)
    args = parser.parse_args()
    torch.set_num_threads(POLICY["threads"])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    {"prepare": prepare, "train": train, "test": final_test}[args.stage]()


if __name__ == "__main__":
    main()
