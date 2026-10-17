"""Independent fixed-weight preparation comparison; no official challenge access."""

from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import time

import numpy as np
from PIL import Image
import torch

from .confidence import measure
from .confidence_broad import font_groups
from .data import load_partition, split_indices
from .highres import render_broad
from .preprocessing_variants import VARIANTS, prepare_variant
from .residual import ResidualCNN
from .supplementary_data import load_partition as load_extra, stratified_split, unique_indices
from .train import ROOT, write_json

NAME = "fixed-weight-preprocessing-v1"
DIRECTORY = ROOT / "artifacts" / NAME
REPORT = ROOT / "reports" / (NAME + ".json")
SEED = 2026102101
POLICY = {"seed": SEED, "development_count": 1800, "clean_guard_count": 5000,
          "variants": list(VARIANTS), "input_side": 64, "threads": 4,
          "weights_fixed": "captcha-v3", "new_model_training": False,
          "official_inputs_labels_generator_or_predictions_used": False,
          "reserved_test": "NOT RUN; no test partition decoded",
          "selection": "Minimum raw validation NLL among variants satisfying all declared gates; otherwise current",
          "gates": {"raw_accuracy_tolerance": .001, "clean_accuracy_tolerance": .001,
                    "strict_correct_90_minimum_gain": .005, "nll_must_improve": True,
                    "brier_tolerance": .001, "ece_tolerance": .005, "confident_error_increase_allowed": 0},
          "threshold": "Correct and original score strictly >0.9; historical >=0.9 fields remain separately named",
          "human_readability_review": "NOT RUN; contact sheet available, generated labels only",
          "prior_exposure": "Historical model and font exposure; new synthetic seeds, not a blind real-CAPTCHA population study"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_measure(model, x, labels):
    metrics, scores = measure(model, x, labels)
    correct = scores.argmax(1) == labels.numpy()
    high = scores.max(1) > .9
    metrics.update(correct_above_90_count=int((correct & high).sum()),
                   correct_above_90_fraction=float((correct & high).mean()),
                   wrong_above_90_count=int((~correct & high).sum()))
    return metrics, scores


def qualifies(candidate, baseline):
    if candidate.get("preprocessing_failures"):
        return False
    gates = POLICY["gates"]
    raw, old = candidate["raw"], baseline["raw"]
    return (raw["accuracy"] >= old["accuracy"] - gates["raw_accuracy_tolerance"]
            and candidate["clean"]["accuracy"] >= baseline["clean"]["accuracy"] - gates["clean_accuracy_tolerance"]
            and raw["correct_above_90_fraction"] >= old["correct_above_90_fraction"] + gates["strict_correct_90_minimum_gain"]
            and raw["loss"] < old["loss"]
            and raw["brier"] <= old["brier"] + gates["brier_tolerance"]
            and raw["ece_10_bins"] <= old["ece_10_bins"] + gates["ece_tolerance"]
            and raw["wrong_above_90_count"] <= old["wrong_above_90_count"])


def prepared(images, variant):
    inputs, failed = [], []
    for index, image in enumerate(images):
        try:
            inputs.append(prepare_variant(np.asarray(image), variant))
        except ValueError:
            failed.append(index)
            inputs.append(np.zeros((1, 64, 64), np.float32))
    return torch.from_numpy(np.stack(inputs)), failed


def figures(records, raw):
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(20, 5, figsize=(13, 32))
    for index in range(20):
        axes[index, 0].imshow(raw[index])
        axes[index, 0].set_title(f"Independent {index:02d} · source label {records[index]['label']}", fontsize=8)
        for col, variant in enumerate(VARIANTS, 1):
            try:
                axes[index, col].imshow(prepare_variant(np.asarray(raw[index]), variant)[0], cmap="gray", vmin=0, vmax=1)
            except ValueError:
                axes[index, col].text(.1, .5, "Preparation failed")
            axes[index, col].set_title(variant, fontsize=8)
        for axis in axes[index]:
            axis.axis("off")
    figure.suptitle("Fixed choices: printed and handwritten classes 0–9; human review NOT RUN", y=.999)
    figure.tight_layout(rect=(0, 0, 1, .99))
    path = ROOT / "reports/screenshots" / (NAME + "-inputs.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=100)
    plt.close(figure)


def main():
    if DIRECTORY.exists() or REPORT.exists():
        raise FileExistsError("Preserve completed preparation study")
    DIRECTORY.mkdir(parents=True)
    torch.set_num_threads(POLICY["threads"])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(SEED)
    source_names = ("preprocessing_study.py", "preprocessing_variants.py", "preprocess.py", "confidence.py",
                    "highres.py", "captcha.py", "model.py", "residual.py", "supplementary_data.py", "emnist_data.py",
                    "data.py", "platform_support.py", "confidence_broad.py", "train.py")
    source_hashes = {name: digest(ROOT / "digitlab" / name) for name in source_names}
    preserved_paths = [*ROOT.glob("dist/v3/*.js"), ROOT / "dist/index.html", ROOT / "artifacts/frozen-app.zip"]
    for folder in (ROOT / "dist/model", ROOT / "dist/model/captcha-v3/digits", ROOT / "dist/model/mnist-supplementary-v1/digits"):
        preserved_paths.extend([folder / "weights.bin", folder / "manifest.json"])
    preserved = {str(p.relative_to(ROOT)): digest(p) for p in preserved_paths}
    metadata = {"status": "PREPARING", "started_utc": datetime.now(timezone.utc).isoformat(), "policy": POLICY,
                "source_sha256": source_hashes, "preserved_sha256": preserved,
                "protocol_sha256": digest(ROOT / "docs/preprocessing-study.md"),
                "environment": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__, "platform": platform.platform()},
                "variants": {}}
    write_json(REPORT, metadata)
    fonts = font_groups(ROOT / "data/open-fonts")
    metadata["fonts_sha256"] = {str(p.relative_to(ROOT)): digest(p) for group in fonts.values() for p in group}
    images, labels = load_extra(True)
    independent = unique_indices(images, [])
    extra_train, extra_validation = stratified_split(labels, independent, seed=SEED)
    metadata["duplicate_source_images_removed"] = len(images) - len(independent)
    mnist, mnist_labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
    mnist_train, mnist_validation = split_indices(mnist_labels)
    np.savez(DIRECTORY / "source-split.npz", emnist_train=extra_train, emnist_development=extra_validation,
             mnist_train=mnist_train, mnist_validation=mnist_validation)
    metadata["source_split_sha256"] = digest(DIRECTORY / "source-split.npz")
    metadata["dataset_sha256"] = json.loads((ROOT / "data/emnist-digits/provenance.json").read_text())["sha256"]
    rng = np.random.default_rng(SEED)
    by_class = {digit: extra_validation[labels[extra_validation] == digit] for digit in range(10)}
    raw, records = [], []
    fixture_folder = DIRECTORY / "fixtures"
    fixture_folder.mkdir()
    print("Rendering balanced independent development data; official files excluded...", flush=True)
    for i in range(POLICY["development_count"]):
        label, printed = i % 10, (i // 10) % 2 == 0
        source_id = int(rng.choice(by_class[label]))
        font = fonts["development"][int(rng.integers(len(fonts["development"])))]
        image = render_broad(rng, label, None if printed else images[source_id], font)
        path = fixture_folder / f"sample-{i:04d}.png"
        image.save(path)
        raw.append(image)
        records.append({"file": path.name, "label": label, "printed": printed,
                        "source_index": None if printed else source_id, "font": str(font.relative_to(ROOT)), "sha256": digest(path)})
    write_json(DIRECTORY / "records.json", records)
    metadata["records_sha256"] = digest(DIRECTORY / "records.json")
    clean = [Image.fromarray(mnist[i]).convert("RGBA") for i in mnist_validation]
    raw_y = torch.tensor([r["label"] for r in records])
    clean_y = torch.from_numpy(mnist_labels[mnist_validation].astype(np.int64))
    model = ResidualCNN()
    model.load_state_dict(torch.load(ROOT / "artifacts/captcha-v3/best.pt", map_location="cpu", weights_only=True))
    blob = b"".join(v.detach().numpy().astype("<f4").tobytes() for v in model.state_dict().values())
    manifest = json.loads((ROOT / "dist/model/captcha-v3/digits/manifest.json").read_text())
    if hashlib.sha256(blob).hexdigest() != manifest["sha256"]:
        raise ValueError("Fixed checkpoint and preserved browser weights differ")
    metadata["model_sha256"] = manifest["sha256"]
    metadata["status"] = "COMPARING FIXED WEIGHTS"
    write_json(REPORT, metadata)
    vectors = {"raw_labels": raw_y.numpy(), "clean_labels": clean_y.numpy()}
    for variant in VARIANTS:
        start = time.perf_counter()
        tx, raw_failed = prepared(raw, variant)
        cx, clean_failed = prepared(clean, variant)
        result = {"preprocessing_failures": len(raw_failed) + len(clean_failed),
                  "raw_failed_indices": raw_failed, "clean_failed_indices": clean_failed}
        if result["preprocessing_failures"]:
            result.update(status="FAIL: preparation failure; no samples omitted", eligible=False)
            metadata["variants"][variant] = result
            if variant == "current":
                raise ValueError("Control preparation failed; preserve failure and investigate dataset")
        else:
            for group, inputs, targets in (("raw", tx, raw_y), ("clean", cx, clean_y)):
                result[group], vectors[variant + "_" + group] = strict_measure(model, inputs, targets)
            result.update(status="MEASURED", seconds=time.perf_counter() - start)
            metadata["variants"][variant] = result
            result["eligible"] = variant != "current" and qualifies(result, metadata["variants"]["current"])
            print(f"{variant}: raw={result['raw']['accuracy']:.3%}, correct >90={result['raw']['correct_above_90_fraction']:.3%}, NLL={result['raw']['loss']:.5f}, clean={result['clean']['accuracy']:.3%}, eligible={result['eligible']}", flush=True)
        write_json(REPORT, metadata)
        del tx, cx
    eligible = [k for k,v in metadata["variants"].items() if v["eligible"]]
    selected = min(eligible, key=lambda k: metadata["variants"][k]["raw"]["loss"]) if eligible else "current"
    metadata.update(selected_variant=selected, status="COMPLETE; " + ("retain current preparation" if not eligible else "development candidate only; browser/reserved test NOT RUN"),
                    completed_utc=datetime.now(timezone.utc).isoformat())
    np.savez_compressed(DIRECTORY / "scores.npz", **vectors)
    metadata["scores_sha256"] = digest(DIRECTORY / "scores.npz")
    metadata["preserved_unchanged"] = all(digest(ROOT / p) == value for p,value in preserved.items())
    metadata["study_sources_unchanged"] = all(digest(ROOT / "digitlab" / p) == value for p,value in source_hashes.items())
    if not metadata["preserved_unchanged"] or not metadata["study_sources_unchanged"]:
        raise ValueError("Preservation or source identity changed")
    write_json(DIRECTORY / "selection.json", {"selected_variant": selected, "policy": POLICY,
               "model_sha256": manifest["sha256"], "reserved_or_official_inputs_used": False})
    write_json(REPORT, metadata)
    figures(records, raw)
    print(metadata["status"], flush=True)


if __name__ == "__main__":
    main()
