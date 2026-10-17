"""Re-evaluate the frozen captcha-v3 CNN on MNIST without modifying experiments.

This is a reproducibility follow-up on previously evaluated data, not selection.
It never imports a challenge collector, reads official challenge images, trains,
exports weights or replaces an existing report.
"""

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dia2-local"
sys.path.insert(0, str(APP))

import numpy as np
import torch
from PIL import __version__ as pillow_version
from digitlab.data import load_partition
from digitlab.preprocess import prepare_mnist
from digitlab.residual import ResidualCNN


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_checkpoint_export(model, manifest, weights):
    if sha(weights) != manifest["sha256"] or weights.stat().st_size != manifest["bytes"]:
        raise ValueError("Browser weights differ from the selected manifest")
    blob = np.frombuffer(weights.read_bytes(), dtype="<f4")
    state = model.state_dict()
    if set(state) != {item["name"] for item in manifest["tensors"]}:
        raise ValueError("Checkpoint/export tensor names differ")
    for item in manifest["tensors"]:
        actual = state[item["name"]].cpu().numpy()
        exported = blob[item["offset"]:item["offset"] + item["length"]].reshape(item["shape"])
        np.testing.assert_array_equal(actual, exported)


def evaluate(model, images, labels, batch_size=256):
    confusion = np.zeros((10, 10), dtype=np.int64)
    loss_sum = 0.0
    predictions = []
    with torch.inference_mode():
        for start in range(0, len(labels), batch_size):
            batch = torch.from_numpy(prepare_mnist(images[start:start + batch_size], 64))
            targets = torch.from_numpy(labels[start:start + batch_size].astype(np.int64))
            logits = model(batch)
            if not torch.isfinite(logits).all():
                raise ValueError("Nonfinite inference logits")
            loss_sum += torch.nn.functional.cross_entropy(logits, targets, reduction="sum").item()
            winners = logits.argmax(1).numpy()
            np.add.at(confusion, (targets.numpy(), winners), 1)
            scores = logits.softmax(1).numpy()
            predictions.extend({"index": start + i, "expected": int(targets[i]),
                                "predicted": int(winner), "scores": scores[i].tolist()}
                               for i, winner in enumerate(winners))
    correct = int(np.trace(confusion))
    return {"count": len(labels), "correct": correct, "accuracy": correct / len(labels),
            "loss": loss_sum / len(labels), "confusion_matrix": confusion.tolist()}, predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    destination = args.report.resolve()
    protected = [APP / "artifacts", APP / "dist", APP / "data", ROOT / "Dia2"]
    if destination.suffix != ".json" or destination.exists() or any(destination.is_relative_to(p.resolve()) for p in protected):
        parser.error("Choose a new JSON report outside frozen artifacts, serving assets and course data")
    checkpoint = APP / "artifacts/captcha-v3/best.pt"
    manifest_path = APP / "dist/model/captcha-v3/digits/manifest.json"
    weights = manifest_path.with_name("weights.bin")
    report_path = APP / "reports/captcha-v3.json"
    preserved = [checkpoint, manifest_path, weights, report_path,
                 APP / "reports/challenge-raw.json", APP / "reports/challenge-freeze.json",
                 APP / "reports/captcha-v3-challenge-freeze.json", APP / "reports/captcha-v3-challenge-raw.json"]
    before = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in preserved}
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL",
              "scope": "Read-only selected-model MNIST reproducibility follow-up; prior test exposure known",
              "environment": {"python": platform.python_version(), "torch": torch.__version__,
                              "numpy": np.__version__, "pillow": pillow_version},
              "preserved_sha256_before": before}
    try:
        torch.set_num_threads(4)
        torch.use_deterministic_algorithms(True)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        identity = json.loads(Path(__file__).with_name("submission-model-identity.json").read_text(encoding="utf-8"))
        if sha(checkpoint) != identity["checkpoint_sha256"] or manifest["sha256"] != identity["model_sha256"]:
            raise ValueError("Selected model identity mismatch")
        model = ResidualCNN()
        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
        model.eval()
        verify_checkpoint_export(model, manifest, weights)
        images, labels = load_partition(ROOT / "Dia2/Dataset-MNIST/data", False)
        metrics, predictions = evaluate(model, images, labels)
        historical = json.loads(report_path.read_text(encoding="utf-8"))["test"]
        if metrics["confusion_matrix"] != historical["confusion_matrix"]:
            raise ValueError("Repeated clean test confusion differs; investigate without tuning")
        if abs(metrics["loss"] - historical["loss"]) > 1e-5:
            raise ValueError("Repeated clean loss exceeds 1e-5 tolerance")
        record.update(metrics=metrics, predictions=predictions, model_sha256=manifest["sha256"],
                      checkpoint_export_tensors_equal=True, historical_confusion_equal=True,
                      loss_absolute_difference=abs(metrics["loss"] - historical["loss"]),
                      test_input_hashes={p.name: sha(p) for p in (ROOT / "Dia2/Dataset-MNIST/data").glob("t10k*.gz")},
                      status="PASS")
    except Exception as error:
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        after = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in preserved}
        record["preserved_sha256_after"] = after
        record["frozen_artifacts_unchanged"] = before == after
        if before != after:
            record["status"] = "FAIL"
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, allow_nan=False)
            stream.write("\n")
    if record["status"] != "PASS":
        raise SystemExit("FAIL: see new report")
    print(f"PASS: {record['metrics']['correct']}/10000 clean MNIST, identical confusion; frozen artifacts unchanged")


if __name__ == "__main__":
    main()
