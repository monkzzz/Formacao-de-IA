"""Independent hard-example replay with a frozen-teacher retention objective."""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import platform
import time

import numpy as np
import torch
from torch.nn import functional as F

from .confidence import digest, measure
from .confidence_broad import font_groups, load_model, update_average
from .confidence_data import make_set
from .data import FILES, load_partition, split_indices
from .preprocess import prepare_mnist
from .residual import make_raw
from .train import ROOT, write_json

NAME = "captcha-confidence-replay-v1"
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
SEED = 2026101817
POLICY = {
    "seed": SEED, "epochs": 4, "raw_training": 4800, "clean_training": 4000,
    "development": 2400, "bridge": 2400, "reserved": 6000,
    "batch_size": 64, "threads": 4, "learning_rate": .00003,
    "minimum_learning_rate": .000005, "ema_decay": .98, "training_dropout": .1,
    "objective": "CE weighted by 1+2*(1-baseline_true_class_score); add 2*KL(baseline||student) only on baseline-correct training examples; teacher frozen",
    "selection": "Lowest raw development NLL among eligible EMA epoch checkpoints; otherwise retain baseline",
    "gates": {"accuracy_loss_limit": .001, "clean_loss_limit": .001, "bridge_loss_limit": .001,
              "minimum_correct_above_90_gain": .005, "brier_increase_limit": .001,
              "ece_increase_limit": .005, "nll_must_improve": True,
              "confident_wrong_count_must_not_increase": True},
    "fonts": "Pinned train/development/test families; fresh seeds and current-run splits, not a claim of no historical font exposure",
    "inference": "Unchanged residual architecture, prepare64 and raw softmax; no score scaling or temperature adjustment",
    "official_inputs_labels_or_previous_predictions_used": False,
}
SOURCES = ("confidence_replay.py", "confidence.py", "confidence_broad.py", "confidence_data.py",
           "residual.py", "highres.py", "captcha.py", "ensemble_benchmark.py", "preprocess.py", "data.py", "model.py")


def replay_loss(logits, labels, teacher):
    true_score = teacher.gather(1, labels[:, None]).squeeze(1)
    weights = 1 + 2 * (1 - true_score)
    ce = (F.cross_entropy(logits, labels, reduction="none") * weights).mean()
    keep = teacher.argmax(1) == labels
    divergence = F.kl_div(logits.log_softmax(1), teacher, reduction="none").sum(1)
    retention = divergence[keep].mean() if keep.any() else divergence.sum() * 0
    return ce + 2 * retention


def metrics(model, x, y):
    result, scores = measure(model, x, y)
    correct = scores.argmax(1) == y.numpy()
    high = scores.max(1) > .9
    result.update(correct_above_90=int((correct & high).sum()),
                  correct_above_90_fraction=float((correct & high).mean()),
                  wrong_above_90=int((~correct & high).sum()))
    return result, scores


def qualifies(candidate, baseline):
    a, b, gates = candidate["raw"], baseline["raw"], POLICY["gates"]
    return (a["accuracy"] >= b["accuracy"] - gates["accuracy_loss_limit"]
            and candidate["clean"]["accuracy"] >= baseline["clean"]["accuracy"] - gates["clean_loss_limit"]
            and candidate["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - gates["bridge_loss_limit"]
            and a["correct_above_90_fraction"] >= b["correct_above_90_fraction"] + gates["minimum_correct_above_90_gain"]
            and a["loss"] < b["loss"]
            and a["brier"] <= b["brier"] + gates["brier_increase_limit"]
            and a["ece_10_bins"] <= b["ece_10_bins"] + gates["ece_increase_limit"]
            and a["wrong_above_90"] <= b["wrong_above_90"])


def verify(metadata):
    for name, checksum in metadata["preserved_sha256"].items():
        if digest(ROOT / name) != checksum:
            raise ValueError("Preserved asset/evidence changed: " + name)
    for name, checksum in metadata["source_sha256"].items():
        if digest(ROOT / "digitlab" / name) != checksum:
            raise ValueError("Experiment source changed: " + name)
    for name, checksum in metadata["font_sha256"].items():
        if digest(ROOT / "data/open-fonts" / name) != checksum:
            raise ValueError("Font changed: " + name)


def train():
    if DIRECTORY.exists() or REPORT.exists():
        raise FileExistsError("Preserve prior experiment")
    fonts = font_groups(ROOT / "data/open-fonts")
    baseline_path = ROOT / "artifacts/captcha-v3/best.pt"
    baseline = load_model(baseline_path).eval()
    manifest = json.loads((ROOT / "dist/model/captcha-v3/digits/manifest.json").read_text())
    exported = b"".join(t.detach().numpy().astype("<f4").tobytes() for t in baseline.state_dict().values())
    if hashlib.sha256(exported).hexdigest() != manifest["sha256"]:
        raise ValueError("Baseline checkpoint differs from preserved browser weights")
    preserved = [baseline_path, ROOT / "artifacts/frozen-app.zip"]
    preserved += [p for p in (ROOT / "dist").rglob("*") if p.is_file() and p.suffix.lower() not in (".sfc", ".smc")]
    preserved += [p for p in (ROOT / "reports").glob("*challenge*.json")]
    metadata = {"status": "PREPARING", "policy": POLICY, "history": [],
                "started_utc": datetime.now(timezone.utc).isoformat(),
                "source_sha256": {n: digest(ROOT / "digitlab" / n) for n in SOURCES},
                "preserved_sha256": {str(p.relative_to(ROOT)): digest(p) for p in preserved},
                "font_sha256": {str(p.relative_to(ROOT / "data/open-fonts")): digest(p) for group in fonts.values() for p in group},
                "environment": {"python": platform.python_version(), "torch": torch.__version__, "platform": platform.platform()},
                "mnist_archives_sha256": {n: digest(ROOT.parent / "Dia2/Dataset-MNIST/data" / n) for n in FILES},
                "official_inference": "NOT RUN", "reserved_test": "NOT RUN"}
    DIRECTORY.mkdir(parents=True)
    write_json(REPORT, metadata)  # Policy and identities are durable before data/model results.
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    training, validation = split_indices(labels)
    np.savez(DIRECTORY / "split.npz", train=training, validation=validation)
    print("Preparing independent training/development images...", flush=True)
    generated = make_set(images, labels, training, fonts["train"], POLICY["raw_training"], SEED,
                         DIRECTORY / "training-fixtures")
    raw_x, raw_y = generated["views"][:, 0].clone(), generated["labels"]
    del generated
    rng = np.random.default_rng(SEED + 1)
    chosen = np.concatenate([rng.choice(training[labels[training] == digit], POLICY["clean_training"] // 10, replace=False) for digit in range(10)])
    tx = torch.cat((raw_x, torch.from_numpy(prepare_mnist(images[chosen], 64))))
    ty = torch.cat((raw_y, torch.from_numpy(labels[chosen].astype(np.int64))))
    del raw_x, raw_y
    development = make_set(images, labels, validation, fonts["development"], POLICY["development"], SEED + 2,
                           DIRECTORY / "development-fixtures")
    vx, vy = development["views"][:, 0].clone(), development["labels"]
    del development
    clean = torch.from_numpy(prepare_mnist(images[validation], 64))
    clean_y = torch.from_numpy(labels[validation].astype(np.int64))
    bridge, bridge_y = make_raw(images, labels, validation, fonts["development"], POLICY["bridge"], SEED + 3)
    torch.save({"training": tx, "training_labels": ty, "development": vx, "development_labels": vy,
                "bridge": bridge, "bridge_labels": bridge_y, "clean": clean, "clean_labels": clean_y}, DIRECTORY / "data.pt")
    metadata["data_sha256"] = digest(DIRECTORY / "data.pt")
    def evaluate(network):
        return {"raw": metrics(network, vx, vy)[0], "clean": metrics(network, clean, clean_y)[0],
                "bridge": metrics(network, bridge, bridge_y)[0]}
    metadata["baseline_validation"] = evaluate(baseline)
    _, teacher_scores = measure(baseline, tx, ty)
    teacher = torch.from_numpy(teacher_scores)
    model, average = copy.deepcopy(baseline), copy.deepcopy(baseline)
    model.dropout.p = POLICY["training_dropout"]
    optimizer = torch.optim.AdamW(model.parameters(), lr=POLICY["learning_rate"], weight_decay=.0001)
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, POLICY["epochs"], eta_min=POLICY["minimum_learning_rate"])
    metadata["status"] = "TRAINING"
    write_json(REPORT, metadata)
    best = float("inf")
    for epoch in range(POLICY["epochs"]):
        started = time.perf_counter()
        model.train()
        order = torch.randperm(len(tx), generator=torch.Generator().manual_seed(SEED + 100 + epoch))
        for start in range(0, len(order), POLICY["batch_size"]):
            ids = order[start:start + POLICY["batch_size"]]
            optimizer.zero_grad(set_to_none=True)
            replay_loss(model(tx[ids]), ty[ids], teacher[ids]).backward()
            optimizer.step()
            update_average(average, model, POLICY["ema_decay"])
        result = evaluate(average)
        passed = qualifies(result, metadata["baseline_validation"])
        if passed and result["raw"]["loss"] < best:
            best = result["raw"]["loss"]
            torch.save(average.state_dict(), DIRECTORY / "best.pt")
            metadata.update(selected_epoch=epoch + 1, validation=result)
        metadata["history"].append({"epoch": epoch + 1, **result, "eligible": passed,
                                    "seconds": time.perf_counter() - started})
        write_json(REPORT, metadata)
        print(f"Epoch {epoch+1}: raw={result['raw']['accuracy']:.3%}, strict coverage={result['raw']['correct_above_90_fraction']:.3%}, NLL={result['raw']['loss']:.5f}, eligible={passed}", flush=True)
        schedule.step()
    torch.save(average.state_dict(), DIRECTORY / "last.pt")
    selection = {"selected_epoch": metadata.get("selected_epoch"), "checkpoint_sha256": digest(DIRECTORY / "best.pt") if "selected_epoch" in metadata else None,
                 "policy": POLICY, "development_report_sha256": None, "reserved_test_opened": False}
    metadata["status"] = "SELECTED; reserved/browser checks NOT RUN" if selection["selected_epoch"] else "RETAIN BASELINE; no eligible epoch"
    metadata["completed_utc"] = datetime.now(timezone.utc).isoformat()
    verify(metadata)
    write_json(REPORT, metadata)
    selection["development_report_sha256"] = digest(REPORT)
    with (DIRECTORY / "selection.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    print(metadata["status"], flush=True)


def test():
    metadata = json.loads(REPORT.read_text())
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    # Reject before loading/decoding canonical test data or rendering reserved images.
    if not selection["selected_epoch"]:
        raise ValueError("No eligible development selection; reserved data remain unopened")
    verify(metadata)
    if digest(REPORT) != selection["development_report_sha256"] or digest(DIRECTORY / "best.pt") != selection["checkpoint_sha256"]:
        raise ValueError("Selected evidence/checkpoint changed")
    with (DIRECTORY / "test-started.json").open("x") as stream:
        json.dump(selection, stream)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    indices = np.arange(len(labels))
    fonts = font_groups(ROOT / "data/open-fonts")["test"]
    generated = make_set(images, labels, indices, fonts, POLICY["reserved"], SEED + 4)
    raw, targets = generated["views"][:, 0].clone(), generated["labels"]
    del generated
    clean, clean_y = torch.from_numpy(prepare_mnist(images, 64)), torch.from_numpy(labels.astype(np.int64))
    bridge, bridge_y = make_raw(images, labels, indices, fonts, POLICY["bridge"], SEED + 5)
    results, scores = {}, {}
    for name, model in (("baseline", load_model(ROOT / "artifacts/captcha-v3/best.pt")), ("candidate", load_model(DIRECTORY / "best.pt"))):
        results[name] = {}
        for kind, x, y in (("raw", raw, targets), ("clean", clean, clean_y), ("bridge", bridge, bridge_y)):
            results[name][kind], scores[name + "_" + kind] = metrics(model, x, y)
    np.savez_compressed(DIRECTORY / "reserved-predictions.npz", **scores, raw_labels=targets.numpy(), clean_labels=clean_y.numpy(), bridge_labels=bridge_y.numpy())
    verify(metadata)
    create = {"status": "PASS" if qualifies(results["candidate"], results["baseline"]) else "RETAIN BASELINE; reserved gates failed",
              "results": results, "selection_sha256": digest(DIRECTORY / "selection.json"),
              "predictions_sha256": digest(DIRECTORY / "reserved-predictions.npz"), "official_inference": "NOT RUN"}
    with (ROOT / "reports" / (NAME + "-reserved.json")).open("x") as stream:
        json.dump(create, stream, indent=2)
    print(create["status"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("train", "test"), required=True)
    args = parser.parse_args()
    torch.set_num_threads(POLICY["threads"])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    {"train": train, "test": test}[args.stage]()


if __name__ == "__main__":
    main()
