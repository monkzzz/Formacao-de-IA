"""Diagnose, train matched consistency/capacity arms, and test one frozen choice."""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
from PIL import __version__ as pillow_version
import torch
from torch.nn import functional as F

from .confidence import POLICY as GATE_POLICY, eligible, measure, score_metrics
from .confidence_broad import font_groups, load_model, update_average
from .confidence_data import CONDITIONS, make_set
from .data import FILES, load_partition, split_indices
from .model import augment
from .preprocess import prepare_mnist
from .residual import ResidualBlock, ResidualCNN, make_raw
from .train import ROOT, write_json

NAME = "captcha-consistency-suite-v1"
SEED = 2026101901
ARMS = ("control", "consistency", "capacity")
DEEP_ARCHITECTURE = "residual64-deep-16-32-128"
POLICY = {
    "seed": SEED, "epochs": 4, "raw_training": 6000, "clean_training": 4000,
    "diagnostic_count": 1200, "development_count": 3600, "bridge_count": 2400,
    "test_count": 6000, "batch_size_sources": 64, "views_per_source": 3, "threads": 4,
    "optimizer": "AdamW lr=0.00015 weight_decay=0.0001; cosine to 0.00001",
    "training_dropout": .15, "ema_decay": .98, "consistency_weight": 3.,
    "arms": {"control": "Existing architecture; CE over three labelled views",
             "consistency": "Existing architecture; same CE plus three-view Jensen-Shannon divergence",
             "capacity": "Two extra identity-initialized residual blocks; same CE and consistency loss"},
    "gates": GATE_POLICY["gates"], "bridge_accuracy_tolerance": .001,
    "selection": "Lowest new-raw development NLL among eligible epochs; prefer smaller network unless deeper improves raw accuracy by .002 or lowers raw NLL by 2% without lowering correct-at-90 coverage",
    "desktop_p95_limit_ms": 150,
    "font_split": "Pinned open fonts: NotoSans/NotoSerif/RobotoSlab/Oswald train, Lato diagnosis/development, Ubuntu final synthetic test",
    "diagnostic_split": "First 250 validation indices of each class for diagnosis; remaining 250 for selection",
    "preprocessing": "Existing production prepare64; annotations and clean pairs are diagnostic/training information only",
    "temperature": 1., "official_inputs_used_for_training_or_selection": False,
    "scope": "Fresh synthetic corruptions; not human-labelled real CAPTCHA population data. Baseline and MNIST have historical evaluations.",
}
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
SOURCE_NAMES = ("confidence_suite.py", "confidence_data.py", "confidence.py", "confidence_broad.py",
                "residual.py", "highres.py", "captcha.py", "ensemble_benchmark.py", "model.py",
                "preprocess.py", "data.py", "platform_support.py")


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class DeeperResidualCNN(ResidualCNN):
    def __init__(self):
        super().__init__()
        self.block3 = ResidualBlock(16)
        self.block4 = ResidualBlock(32)

    def features(self, x):
        first = self.block3(self.block1(F.max_pool2d(F.relu(self.conv1(x)), 2)))
        second = F.avg_pool2d(F.max_pool2d(F.relu(self.conv2(first)), 2), 2)
        second = self.block4(self.block2(second))
        return first, second, F.relu(self.fc1(second.flatten(1)))


def make_model(arm, state):
    model = DeeperResidualCNN() if arm == "capacity" else ResidualCNN()
    missing = model.load_state_dict(state, strict=arm != "capacity")
    if arm == "capacity" and (missing.unexpected_keys or
                              any(not k.startswith(("block3.", "block4.")) for k in missing.missing_keys)):
        raise ValueError("Unexpected capacity initialization mismatch")
    model.dropout.p = POLICY["training_dropout"]
    return model


def consistency_loss(logits):
    if logits.ndim != 3 or logits.shape[1] != 3 or logits.shape[2] != 10:
        raise ValueError("Require Bx3x10 view logits")
    log_probabilities = logits.log_softmax(-1)
    log_mean = torch.logsumexp(log_probabilities, dim=1, keepdim=True) - math.log(3)
    return (log_probabilities.exp() * (log_probabilities - log_mean)).sum(-1).mean()


def save_set(name, data):
    path = DIRECTORY / (name + ".npz")
    with path.open("xb") as stream:
        np.savez(stream, views=data["views"].numpy(), labels=data["labels"].numpy(),
                 conditions=data["conditions"], printed=data["printed"])
    write_json(DIRECTORY / (name + "-records.json"), data["records"])
    return {"file": path.name, "sha256": digest(path), "count": len(data["labels"])}


def read_set(name, metadata):
    record = metadata["datasets"][name]
    path = DIRECTORY / record["file"]
    if digest(path) != record["sha256"]:
        raise ValueError(f"Changed dataset: {name}")
    with np.load(path, allow_pickle=False) as data:
        return {"views": torch.from_numpy(data["views"]), "labels": torch.from_numpy(data["labels"]),
                "conditions": data["conditions"], "printed": data["printed"]}


def subset_metrics(scores, labels, conditions, printed):
    labels = np.asarray(labels)
    return {**{name: score_metrics(scores[conditions == name], labels[conditions == name])
               for name in CONDITIONS if (conditions == name).any()},
            **{name: score_metrics(scores[printed == value], labels[printed == value])
               for name, value in (("printed", True), ("handwritten", False))}}


def baseline_model():
    model = load_model(ROOT / "artifacts/captcha-v3/best.pt")
    blob = b"".join(t.detach().numpy().astype("<f4").tobytes() for t in model.state_dict().values())
    manifest = json.loads((ROOT / "dist/model/captcha-v3/digits/manifest.json").read_text())
    if hashlib.sha256(blob).hexdigest() != manifest["sha256"]:
        raise ValueError("Baseline does not match preserved browser weights")
    return model


def verify_sources(metadata):
    if any(digest(ROOT / "digitlab" / name) != value for name, value in metadata["source_sha256"].items()):
        raise ValueError("Sources changed since protocol/dataset preparation")
    if digest(ROOT / "artifacts/captcha-v3/best.pt") != metadata["baseline_checkpoint_sha256"]:
        raise ValueError("Baseline checkpoint changed")
    for group in metadata["font_sha256"].values():
        if any(digest(ROOT / "data/open-fonts" / name) != value for name, value in group.items()):
            raise ValueError("Font identity changed")


def diagnostic_report(baseline, data):
    raw, noisy_scores = measure(baseline, data["views"][:, 0], data["labels"])
    clean, clean_scores = measure(baseline, data["views"][:, 2], data["labels"])
    y = data["labels"].numpy()
    records = []
    for i, annotation in enumerate(data["records"]):
        records.append({**annotation, "noisy_prediction": int(noisy_scores[i].argmax()),
                        "noisy_top_score": float(noisy_scores[i].max()),
                        "clean_prediction": int(clean_scores[i].argmax()),
                        "clean_top_score": float(clean_scores[i].max())})
    report = {"scope": "Independent synthetic diagnostic split; clean input is an oracle ablation, not deployable cleanup",
              "production_preprocessing": raw, "clean_source_ablation": clean,
              "per_condition": subset_metrics(noisy_scores, y, data["conditions"], data["printed"]),
              "annotation_summary": {}, "records": records}
    for key in ("crop_glyph_mass_retained", "crop_area_over_glyph_box", "glyph_long_side_after_resize"):
        values = np.array([r[key] for r in records])
        report["annotation_summary"][key] = {"mean": float(values.mean()),
                                                   "p10": float(np.quantile(values, .1)),
                                                   "p50": float(np.median(values)), "p90": float(np.quantile(values, .9))}
    report["glyph_under_32_pixels_fraction"] = float(np.mean([r["glyph_long_side_after_resize"] < 32 for r in records]))
    report["clean_correct_noisy_wrong"] = int(((clean_scores.argmax(1) == y) & (noisy_scores.argmax(1) != y)).sum())
    report["noisy_correct_clean_wrong"] = int(((noisy_scores.argmax(1) == y) & (clean_scores.argmax(1) != y)).sum())
    write_json(ROOT / "reports" / (NAME + "-diagnostic.json"), report)
    # The figure is a scientific diagnostic, with fixed examples from each condition.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    indices = [next(i for i, row in enumerate(records) if row["condition"] == condition
                    and row["label"] == digit and row["printed"] == printed)
               for condition in CONDITIONS for digit, printed in ((2, True), (5, False))]
    figure, axes = plt.subplots(len(indices), 4, figsize=(9, 2 * len(indices)))
    fixtures = DIRECTORY / "diagnostic-fixtures"
    for row, i in enumerate(indices):
        prefix = fixtures / f"sample-{i:03d}"
        images = [Image.open(str(prefix) + "-raw.png"), Image.open(str(prefix) + "-mask.png"),
                  data["views"][i, 0, 0].numpy(), data["views"][i, 2, 0].numpy()]
        for column, image in enumerate(images):
            axes[row, column].imshow(image, cmap="gray", vmin=0, vmax=1 if column >= 2 else 255)
            axes[row, column].axis("off")
        axes[row, 0].set_title(f"{records[i]['condition']}; label {records[i]['label']}", fontsize=9)
        axes[row, 2].set_title(f"Raw score {100 * records[i]['noisy_top_score']:.1f}%", fontsize=9)
        axes[row, 3].set_title(f"Clean score {100 * records[i]['clean_top_score']:.1f}%", fontsize=9)
    figure.suptitle("Raw image | annotated glyph | production 64px | clean-source 64px")
    figure.tight_layout()
    destination = ROOT / "reports/screenshots" / (NAME + "-diagnostic.png")
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=110)
    plt.close(figure)
    return {"raw_accuracy": raw["accuracy"], "clean_accuracy": clean["accuracy"],
            "glyph_under_32_pixels_fraction": report["glyph_under_32_pixels_fraction"]}


def prepare_data():
    if DIRECTORY.exists() or REPORT.exists():
        raise FileExistsError("Preserve previous suite; its destination already exists")
    DIRECTORY.mkdir(parents=True)
    fonts = font_groups(ROOT / "data/open-fonts")
    metadata = {"status": "PREPARING", "started_utc": datetime.now(timezone.utc).isoformat(),
                "policy": POLICY, "datasets": {}, "arms": {},
                "source_sha256": {name: digest(ROOT / "digitlab" / name) for name in SOURCE_NAMES},
                "baseline_checkpoint_sha256": digest(ROOT / "artifacts/captcha-v3/best.pt"),
                "font_sha256": {name: {str(p.relative_to(ROOT / "data/open-fonts")): digest(p) for p in paths}
                                for name, paths in fonts.items()},
                "environment": {"python": platform.python_version(), "torch": torch.__version__,
                                "numpy": np.__version__, "pillow": pillow_version, "platform": platform.platform()},
                "mnist_archives_sha256": {n: digest(ROOT.parent / "Dia2/Dataset-MNIST/data" / n) for n in FILES},
                "preservation": {str(p.relative_to(ROOT)): digest(p) for p in [
                    ROOT / "artifacts/captcha-v3/best.pt", ROOT / "artifacts/frozen-app.zip",
                    *sorted((ROOT / "dist").rglob("*.js")), *sorted((ROOT / "dist").rglob("*.html")),
                    ROOT / "dist/model/captcha-v3/digits/weights.bin",
                    ROOT / "dist/model/captcha-v3/digits/manifest.json",
                    ROOT / "reports/challenge-raw.json", ROOT / "reports/challenge-freeze.json",
                    ROOT / "reports/captcha-confidence-broad-v1.json"] if p.is_file()}}
    write_json(REPORT, metadata)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    train, validation = split_indices(labels)
    diagnostic = np.concatenate([validation[labels[validation] == digit][:250] for digit in range(10)])
    selection = np.setdiff1d(validation, diagnostic)
    assert not set(train) & set(validation) and not set(diagnostic) & set(selection)
    np.savez(DIRECTORY / "splits.npz", train=train, diagnostic=diagnostic, selection=selection)
    metadata["splits_sha256"] = digest(DIRECTORY / "splits.npz")
    baseline = baseline_model()
    for name, ids, group, count, seed in (
            ("diagnostic", diagnostic, "development", POLICY["diagnostic_count"], SEED + 1),
            ("development", selection, "development", POLICY["development_count"], SEED + 2),
            ("training", train, "train", POLICY["raw_training"], SEED + 3)):
        print(f"Preparing {name}: {count} independent paired examples...", flush=True)
        data = make_set(images, labels, ids, fonts[group], count, seed,
                        DIRECTORY / (name + "-fixtures") if name != "training" else None,
                        annotations=name == "diagnostic")
        if name == "diagnostic":
            metadata["diagnosis"] = diagnostic_report(baseline, data)
        if name == "training":
            rng = np.random.default_rng(SEED + 4)
            chosen = np.concatenate([rng.choice(train[labels[train] == digit], POLICY["clean_training"] // 10,
                                                replace=False) for digit in range(10)])
            clean = torch.from_numpy(prepare_mnist(images[chosen], 64))
            data["views"] = torch.cat((data["views"], clean[:, None].repeat(1, 3, 1, 1, 1)))
            data["labels"] = torch.cat((data["labels"], torch.from_numpy(labels[chosen].astype(np.int64))))
            data["conditions"] = np.concatenate((data["conditions"], np.full(len(chosen), "canonical_clean")))
            data["printed"] = np.concatenate((data["printed"], np.zeros(len(chosen), dtype=bool)))
            data["records"] += [{"source_index": int(i), "label": int(labels[i]), "condition": "canonical_clean"} for i in chosen]
        metadata["datasets"][name] = save_set(name, data)
        write_json(REPORT, metadata)
        del data
    clean = torch.from_numpy(prepare_mnist(images[validation], 64))
    bridge, bridge_y = make_raw(images, labels, selection, fonts["development"], POLICY["bridge_count"], SEED + 5)
    with (DIRECTORY / "validation-extra.npz").open("xb") as stream:
        np.savez(stream, clean=clean.numpy(), labels=labels[validation].astype(np.int64),
                 bridge=bridge.numpy(), bridge_labels=bridge_y.numpy())
    metadata["extra_sha256"] = digest(DIRECTORY / "validation-extra.npz")
    metadata["status"] = "PREPARED; training/test NOT RUN"
    write_json(REPORT, metadata)
    print(json.dumps({"status": metadata["status"], "diagnosis": metadata["diagnosis"]}), flush=True)


def measure_all(model, development, extra):
    return {"raw": measure(model, development["views"][:, 0], development["labels"])[0],
            "clean": measure(model, extra["clean"], extra["labels"])[0],
            "bridge": measure(model, extra["bridge"], extra["bridge_labels"])[0]}


def qualifies(candidate, baseline):
    return (eligible(candidate, baseline)
            and candidate["bridge"]["accuracy"] >= baseline["bridge"]["accuracy"] - POLICY["bridge_accuracy_tolerance"])


def choose_arm(results):
    small = [name for name in ("control", "consistency") if results[name].get("selected_epoch")]
    chosen = min(small, key=lambda name: results[name]["validation"]["raw"]["loss"]) if small else None
    deep = results["capacity"]
    if deep.get("selected_epoch"):
        if chosen is None:
            return "capacity"
        a, b = deep["validation"]["raw"], results[chosen]["validation"]["raw"]
        if (a["accuracy"] >= b["accuracy"] + .002 or
                (a["loss"] <= .98 * b["loss"] and a["correct_at_90_fraction"] >= b["correct_at_90_fraction"])):
            return "capacity"
    return chosen


def train():
    metadata = json.loads(REPORT.read_text())
    if metadata["status"] != "PREPARED; training/test NOT RUN" or metadata["arms"]:
        raise ValueError("Training requires a fresh prepared suite")
    verify_sources(metadata)
    if digest(DIRECTORY / "validation-extra.npz") != metadata["extra_sha256"]:
        raise ValueError("Validation cache changed")
    development = read_set("development", metadata)
    training = read_set("training", metadata)
    with np.load(DIRECTORY / "validation-extra.npz", allow_pickle=False) as cache:
        extra = {name: torch.from_numpy(cache[name]) for name in cache.files}
    baseline = baseline_model()
    metadata["baseline_validation"] = measure_all(baseline, development, extra)
    metadata["status"] = "TRAINING"
    write_json(REPORT, metadata)
    for arm in ARMS:
        torch.manual_seed(SEED + 100)
        model = make_model(arm, baseline.state_dict())
        average = copy.deepcopy(model)
        torch.manual_seed(SEED + 101)
        optimizer = torch.optim.AdamW(model.parameters(), lr=.00015, weight_decay=.0001)
        schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, POLICY["epochs"], eta_min=.00001)
        result = {"history": [], "parameter_count": sum(p.numel() for p in model.parameters()),
                  "objective": POLICY["arms"][arm]}
        metadata["arms"][arm] = result
        best = float("inf")
        for epoch in range(POLICY["epochs"]):
            started = time.perf_counter()
            model.train()
            generator = torch.Generator().manual_seed(SEED + 200 + epoch)
            order = torch.randperm(len(training["labels"]), generator=generator)
            ce_total, js_total = 0., 0.
            for begin in range(0, len(order), POLICY["batch_size_sources"]):
                ids = order[begin:begin + POLICY["batch_size_sources"]]
                batch = training["views"][ids].reshape(-1, 1, 64, 64)
                labels = training["labels"][ids]
                optimizer.zero_grad(set_to_none=True)
                logits = model(augment(batch)).reshape(len(ids), 3, 10)
                ce = F.cross_entropy(logits.reshape(-1, 10), labels.repeat_interleave(3))
                js = consistency_loss(logits)
                loss = ce + (0 if arm == "control" else POLICY["consistency_weight"]) * js
                loss.backward()
                optimizer.step()
                update_average(average, model, POLICY["ema_decay"])
                ce_total += ce.item() * len(ids)
                js_total += js.item() * len(ids)
            metrics = measure_all(average, development, extra)
            passes = qualifies(metrics, metadata["baseline_validation"])
            if passes and metrics["raw"]["loss"] < best:
                best = metrics["raw"]["loss"]
                torch.save(average.state_dict(), DIRECTORY / (arm + "-best.pt"))
                result.update(selected_epoch=epoch + 1, validation=metrics)
            result["history"].append({"epoch": epoch + 1, **metrics, "eligible": passes,
                                      "training_ce": ce_total / len(order), "training_js": js_total / len(order),
                                      "seconds": time.perf_counter() - started})
            write_json(REPORT, metadata)
            print(f"{arm} epoch {epoch+1}: raw={metrics['raw']['accuracy']:.3%}, correct-at-90={metrics['raw']['correct_at_90_fraction']:.3%}, clean={metrics['clean']['accuracy']:.3%}, bridge={metrics['bridge']['accuracy']:.3%}, NLL={metrics['raw']['loss']:.5f}, eligible={passes}, {time.perf_counter()-started:.1f}s", flush=True)
            schedule.step()
        torch.save(average.state_dict(), DIRECTORY / (arm + "-last.pt"))
    chosen = choose_arm(metadata["arms"])
    frozen_report = DIRECTORY / "development-report.json"
    with frozen_report.open("x") as stream:
        json.dump(metadata, stream, indent=2)
    selection = {"arm": chosen, "policy": POLICY, "test_loaded": False,
                 "selected_epoch": metadata["arms"][chosen]["selected_epoch"] if chosen else None,
                 "checkpoint_sha256": digest(DIRECTORY / (chosen + "-best.pt")) if chosen else None,
                 "source_sha256": metadata["source_sha256"], "development_report_sha256": digest(frozen_report)}
    with (DIRECTORY / "selection.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    metadata["selected_arm"] = chosen
    metadata["status"] = "SELECTED; browser/final test NOT RUN" if chosen else "RETAIN BASELINE; no eligible arm"
    metadata["training_completed_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(REPORT, metadata)
    print(metadata["status"], chosen, flush=True)


def load_selection():
    metadata = json.loads(REPORT.read_text())
    verify_sources(metadata)
    selection = json.loads((DIRECTORY / "selection.json").read_text())
    if not selection["arm"]:
        raise ValueError("No eligible development selection; reserved data remain unopened")
    if digest(DIRECTORY / "development-report.json") != selection["development_report_sha256"]:
        raise ValueError("Frozen development evidence changed")
    if digest(DIRECTORY / (selection["arm"] + "-best.pt")) != selection["checkpoint_sha256"]:
        raise ValueError("Selected checkpoint changed")
    model = make_model(selection["arm"], baseline_model().state_dict())
    model.load_state_dict(torch.load(DIRECTORY / (selection["arm"] + "-best.pt"), map_location="cpu", weights_only=True))
    return metadata, selection, model


def final_test():
    metadata, selection, model = load_selection()
    if "test" in metadata:
        raise ValueError("Preserve completed final test")
    browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    if (browser["status"] != "PASS" or browser["checkpoint_sha256"] != selection["checkpoint_sha256"]
            or browser["latency_p95_ms"] >= POLICY["desktop_p95_limit_ms"]):
        raise ValueError("Require selected-model browser parity and speed before final test")
    with (DIRECTORY / "test-started.json").open("x") as stream:
        json.dump(selection, stream, indent=2)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    fonts = font_groups(ROOT / "data/open-fonts")["test"]
    data = make_set(images, labels, np.arange(len(labels)), fonts, POLICY["test_count"], SEED + 6,
                    DIRECTORY / "test-fixtures")
    clean = torch.from_numpy(prepare_mnist(images, 64))
    targets = torch.from_numpy(labels.astype(np.int64))
    bridge, bridge_y = make_raw(images, labels, np.arange(len(labels)), fonts, POLICY["bridge_count"], SEED + 7)
    results, vectors = {}, {}
    for name, network in (("baseline", baseline_model()), ("candidate", model)):
        raw, scores = measure(network, data["views"][:, 0], data["labels"])
        results[name] = {"raw": raw, "clean": measure(network, clean, targets)[0],
                         "bridge": measure(network, bridge, bridge_y)[0],
                         "per_condition": subset_metrics(scores, data["labels"].numpy(), data["conditions"], data["printed"])}
        vectors[name] = scores
    np.savez(DIRECTORY / "test-predictions.npz", **vectors, labels=data["labels"].numpy())
    y = data["labels"].numpy()
    old, new = vectors["baseline"].argmax(1) == y, vectors["candidate"].argmax(1) == y
    metadata["test"] = results
    metadata["paired_comparison"] = {"candidate_only_correct": int((new & ~old).sum()),
                                      "baseline_only_correct": int((old & ~new).sum())}
    metadata["independent_test_eligible"] = qualifies(results["candidate"], results["baseline"])
    metadata["status"] = "PASS: reserved gates; official follow-up NOT RUN" if metadata["independent_test_eligible"] else "RETAIN BASELINE: reserved gate failed"
    write_json(REPORT, metadata)
    print(json.dumps({"status": metadata["status"], "test": results, "paired": metadata["paired_comparison"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("prepare", "train", "test"), required=True)
    args = parser.parse_args()
    torch.set_num_threads(POLICY["threads"])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    {"prepare": prepare_data, "train": train, "test": final_test}[args.stage]()


if __name__ == "__main__":
    main()
