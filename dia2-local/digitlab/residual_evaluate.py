"""Export a frozen development choice, then open fresh test data after speed QA."""

import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
from PIL import Image, __version__ as pillow_version
import torch

from .data import load_partition, split_indices
from .highres import HighResCNN, export
from .preprocess import prepare, prepare_mnist
from .residual import ARCHITECTURE, NAME, POLICY, SEED, TEST_FONTS, ResidualCNN, make_raw
from .robust import evaluate
from .train import ROOT, write_json


def run(stage):
    torch.set_num_threads(4)
    directory = ROOT / "artifacts" / NAME
    report_path = ROOT / "reports" / f"{NAME}.json"
    metadata = json.loads(report_path.read_text())
    selection = json.loads((directory / "selection.json").read_text())
    assert selection["selected_epoch"] and metadata["selected_epoch"] == selection["selected_epoch"]
    checkpoint = directory / "best.pt"
    model = ResidualCNN()
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    model.eval()
    destination = ROOT / "dist/model" / NAME / "digits"
    if stage == "export":
        assert metadata["status"].startswith("SELECTED")
        _, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", True)
        train, validation = split_indices(labels)
        metadata["split"] = {"train": len(train), "validation": len(validation)}
        metadata["environment"] = {"python": platform.python_version(), "torch": torch.__version__,
                                   "numpy": np.__version__, "pillow": pillow_version, "device": "cpu"}
        assert metadata["generator_sha256"] == hashlib.sha256((ROOT / "digitlab/residual.py").read_bytes()).hexdigest()
        metadata["parameter_count"] = sum(p.numel() for p in model.parameters())
        metadata["source_sha256"] = {name: hashlib.sha256((ROOT / "digitlab" / name).read_bytes()).hexdigest()
            for name in ("residual.py", "captcha.py", "highres.py", "ensemble_benchmark.py", "preprocess.py", "model.py", "data.py")}
        # Existing non-challenge fixtures, not the fresh held-out test split.
        inputs = torch.from_numpy(np.stack([prepare(np.asarray(Image.open(
            ROOT / f"reports/mnist-fixtures/digit-{i}.png").convert("RGBA")), 64) for i in range(10)]))
        manifest = export(model, destination, metadata, inputs)
        manifest["architecture"] = ARCHITECTURE
        write_json(destination / "manifest.json", manifest)
        selection.update(model_sha256=manifest["sha256"],
                         checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest())
        metadata["model_sha256"] = manifest["sha256"]
        write_json(report_path, metadata)
        selection["development_report_sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
        write_json(directory / "selection.json", selection)
        print(f"Exported frozen development selection: {manifest['sha256']}")
        return
    assert "test" not in metadata, "Preserve completed test"
    speed = json.loads((ROOT / "reports/captcha-v3-speed-qa.json").read_text())
    manifest = json.loads((destination / "manifest.json").read_text())
    assert speed["status"] == "PASS" and speed["model_sha256"] == selection["model_sha256"] == manifest["sha256"]
    assert speed["latency"]["candidate"]["p95_ms"] < POLICY["desktop_p95_limit_ms"]
    assert selection["checkpoint_sha256"] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert selection["development_report_sha256"] == hashlib.sha256(report_path.read_bytes()).hexdigest()
    assert all(hashlib.sha256((ROOT / "digitlab" / name).read_bytes()).hexdigest() == value
               for name, value in metadata["source_sha256"].items())
    assert hashlib.sha256((destination / "weights.bin").read_bytes()).hexdigest() == manifest["sha256"]
    with (directory / "test-started.json").open("x", encoding="utf-8") as handle:
        json.dump({"model_sha256": manifest["sha256"], "selection": selection,
                   "speed_report_sha256": hashlib.sha256((ROOT / "reports/captcha-v3-speed-qa.json").read_bytes()).hexdigest()}, handle, indent=2)
    images, labels = load_partition(ROOT.parent / "Dia2/Dataset-MNIST/data", False)
    clean = torch.from_numpy(prepare_mnist(images, 64))
    targets = torch.from_numpy(labels.astype(np.int64))
    fonts = [Path("C:/Windows/Fonts") / name for name in TEST_FONTS]
    print("Opening fresh 20,000-image synthetic test, with separate font families...", flush=True)
    raw, raw_y = make_raw(images, labels, np.arange(len(labels)), fonts, POLICY["test_count"], SEED + 2,
                          directory / "fixtures")
    baseline = HighResCNN()
    baseline.load_state_dict(torch.load(ROOT / "artifacts/captcha-v2/best.pt", map_location="cpu", weights_only=True))
    metadata["test"], metadata["raw_test"] = evaluate(model, clean, targets), evaluate(model, raw, raw_y)
    metadata["baseline_test"] = {"clean": evaluate(baseline, clean, targets), "raw": evaluate(baseline, raw, raw_y)}
    metadata["test_font_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in fonts}
    predictions = []
    for network in (baseline, model):
        network.eval()
        with torch.no_grad():
            predictions.append(torch.cat([network(raw[i:i + 256]).argmax(1)
                                           for i in range(0, len(raw), 256)]).numpy())
    actual = raw_y.numpy()
    old_correct, new_correct = predictions[0] == actual, predictions[1] == actual
    fixes = int((~old_correct & new_correct).sum())
    breaks = int((old_correct & ~new_correct).sum())
    # Paired bootstrap on correct/incorrect disagreements, with a fixed seed.
    draws = np.random.default_rng(SEED + 3).multinomial(len(actual),
        [fixes / len(actual), breaks / len(actual), 1 - (fixes + breaks) / len(actual)], size=10000)
    metadata["paired_raw_comparison"] = {"fixes": fixes, "breaks": breaks,
        "net_correct_gain": fixes - breaks,
        "accuracy_gain_95_percent_bootstrap_interval": np.quantile((draws[:, 0] - draws[:, 1]) / len(actual), [.025, .975]).tolist(),
        "scope": "Diagnostic paired interval on this synthetic sample; not an additional selection gate"}
    np.savez_compressed(directory / "test-predictions.npz", baseline=predictions[0], candidate=predictions[1], labels=actual)
    eligible = (metadata["test"]["accuracy"] >= metadata["baseline_test"]["clean"]["accuracy"] - POLICY["clean_tolerance"]
                and metadata["raw_test"]["accuracy"] >= metadata["baseline_test"]["raw"]["accuracy"] + POLICY["minimum_raw_gain"])
    metadata["deployment_eligible"] = eligible
    metadata["status"] = "PASS: fresh test gate; full UI QA pending" if eligible else "RETAIN BASELINE: fresh test gate failed"
    write_json(report_path, metadata)
    manifest["training"] = metadata
    write_json(destination / "manifest.json", manifest)
    print(json.dumps({"status": metadata["status"], "candidate_clean": metadata["test"]["accuracy"],
                      "candidate_raw": metadata["raw_test"]["accuracy"], "baseline": metadata["baseline_test"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=("export", "test"))
    run(parser.parse_args().stage)
