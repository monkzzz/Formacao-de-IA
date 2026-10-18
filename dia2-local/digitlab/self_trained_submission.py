"""Build a separate submission using verified locally trained weights only."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import numpy as np
import torch

from .train import ROOT, write_json

NAME = "self-trained-submission-v1"
DEFAULT_OUTPUT = ROOT / "artifacts" / NAME / "site"
SPECS = {
    "mnist": {"folder": "model", "checkpoint": "artifacts/best.pt", "report": "training.json",
              "scope": "Required course model: trained from random initialization on MNIST only, with training-only augmentation.", "dataset": "MNIST"},
    "mnist-supplementary-v1": {"folder": "model/mnist-supplementary-v1/digits", "checkpoint": "artifacts/mnist-supplementary-v1/best.pt", "report": "mnist-supplementary-v1.json",
              "scope": "Optional extension: our MNIST model further trained on MNIST, EMNIST Digits and independently generated synthetic digits.", "dataset": "MNIST"},
    "captcha-v3": {"folder": "model/captcha-v3/digits", "checkpoint": "artifacts/captcha-v3/best.pt", "report": "captcha-v3.json",
              "scope": "Optional residual extension: our original MNIST model, followed by local robustness, synthetic CAPTCHA and 64px residual training.", "dataset": "MNIST"},
    "letters": {"folder": "model/robust/letters", "checkpoint": "artifacts/robust/letters/best.pt", "report": "robust-letters.json",
              "scope": "Optional letters extension: our EMNIST Letters CNN trained from random initialization, then locally trained for robustness.", "dataset": "EMNIST Letters"},
}
EDGES = (("robust-digits", "artifacts/best.pt"),
         ("captcha-v1", "artifacts/robust/digits/best.pt"),
         ("captcha-v2", "artifacts/captcha-v1/best.pt"),
         ("captcha-v3", "artifacts/captcha-v2/best.pt"),
         ("robust-letters", "artifacts/letters/best.pt"))
TRAINING_SOURCES = ("train.py", "model.py", "letters.py", "robust.py", "captcha.py", "highres.py", "residual.py", "supplementary.py", "supplementary_data.py", "data.py", "emnist_data.py", "preprocess.py")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_weights(folder, checkpoint):
    """Verify browser bytes and every tensor against the local training checkpoint."""
    manifest = json.loads((folder / "manifest.json").read_text())
    blob = (folder / "weights.bin").read_bytes()
    if len(blob) != manifest["bytes"] or hashlib.sha256(blob).hexdigest() != manifest["sha256"]:
        raise ValueError("Exported weight integrity mismatch")
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if set(state) != {t["name"] for t in manifest["tensors"]}:
        raise ValueError("Checkpoint and export tensor names differ")
    cursor = 0
    for spec in manifest["tensors"]:
        tensor = state[spec["name"]].detach().numpy().astype("<f4")
        if list(tensor.shape) != spec["shape"] or tensor.size != spec["length"] or spec["offset"] != cursor:
            raise ValueError("Checkpoint/export tensor contract mismatch")
        part = blob[4 * cursor:4 * (cursor + tensor.size)]
        if part != tensor.tobytes():
            raise ValueError("Export does not match local checkpoint tensors")
        cursor += tensor.size
    if cursor * 4 != len(blob):
        raise ValueError("Unexpected exported weight payload")
    return manifest


def provenance():
    edges = []
    for report, parent in EDGES:
        metadata = json.loads((ROOT / "reports" / (report + ".json")).read_text())
        actual = digest(ROOT / parent)
        if actual != metadata["baseline_checkpoint_sha256"]:
            raise ValueError("Recorded training ancestry mismatch: " + report)
        edges.append({"training_stage": report, "local_parent_checkpoint": parent,
                      "parent_sha256": actual, "matches_recorded_parent": True,
                      "report_sha256": digest(ROOT / "reports" / (report + ".json"))})
    models = {}
    for name, spec in SPECS.items():
        manifest = verified_weights(ROOT / "dist" / spec["folder"], ROOT / spec["checkpoint"])
        models[name] = {"scope": spec["scope"], "exported_weights_sha256": manifest["sha256"],
                        "checkpoint_sha256": digest(ROOT / spec["checkpoint"]),
                        "checkpoint_matches_all_exported_tensors": True,
                        "training_report": spec["report"], "training_report_sha256": digest(ROOT / "reports" / spec["report"]),
                        "architecture": manifest["architecture"]}
    # The optional supplementary branch explicitly loads the original local export.
    supplementary = json.loads((ROOT / "reports/mnist-supplementary-v1.json").read_text())
    sources = {name: digest(ROOT / "digitlab" / name) for name in TRAINING_SOURCES}
    roots = {"mnist": {"source": "digitlab/train.py", "initialization": "DigitCNN() with fixed seed; no pretrained parameter supplied", "seed": 20261016},
             "letters": {"source": "digitlab/letters.py", "initialization": "LetterCNN() with fixed seed; no pretrained parameter supplied", "seed": 20261017}}
    return {"status": "PASS", "scope": "Local checkpoint/export identity and recorded training ancestry; source/log audit, not independent proof of authorship",
            "models": models, "random_initialization_roots": roots, "local_parent_edges": edges,
            "supplementary_parent": {"source": "digitlab/supplementary.py:original_model", "parent": "mnist",
                                     "selected_epoch": supplementary["selected_epoch"]},
            "training_source_sha256": sources, "pretrained_external_weights_included": False,
            "network_access_during_build": False, "datasets": "MNIST/EMNIST are downloaded datasets, not pretrained models",
            "official_inputs_used_for_this_build_or_training_audit": False,
            "limitation": "Historical official results are follow-ups after prior exposure; no fresh CAPTCHA inference in this build"}


def build(output=DEFAULT_OUTPUT):
    output = Path(output).resolve()
    source = ROOT / "dist"
    if output.exists() or output == ROOT or source == output or source in output.parents or output in ROOT.parents:
        raise ValueError("Use a new separate output directory; preserve the active app")
    audit = provenance()
    preserved = {str(p.relative_to(ROOT)): digest(p) for p in source.rglob("*") if p.is_file() and p.suffix in (".js", ".html", ".css", ".bin", ".json")}
    output.mkdir(parents=True)
    for name in ("index.html", "submission.js", "submission.css"):
        shutil.copy2(ROOT / "submission" / name, output / name)
    for name in ("inference.js", "preprocess.js", "residual.js", "canvas-tools.js"):
        (output / "v3").mkdir(exist_ok=True)
        shutil.copy2(source / "v3" / name, output / "v3" / name)
    previous = json.loads((ROOT / "reports/selectable-models-challenge-followup-v1-comparison.json").read_text())
    evaluation = {"scope": "Recorded evaluations only; no new test or official inference performed by this builder",
                  "professor_requirement": "Exactly 10/10 correct and every original score strictly >90%; currently unmet", "models": {}}
    for name, spec in SPECS.items():
        folder = output / spec["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        for asset in ("manifest.json", "weights.bin", "parity.json"):
            shutil.copy2(source / spec["folder"] / asset, folder / asset)
        manifest = json.loads((folder / "manifest.json").read_text())
        test = manifest["training"]["test"]
        official = None
        if name != "letters":
            recorded = previous["models"][name]
            official = {"correct": recorded["correct"], "correct_above_90": sum(r["correct"] and r["expected_class_score"] > .9 for r in recorded["cases"]),
                        "scope": "Historical frozen follow-up; not a fresh blind test", "source_report_sha256": digest(ROOT / "reports/selectable-models-challenge-followup-v1-comparison.json")}
        evaluation["models"][name] = {"scope": spec["scope"], "dataset": spec["dataset"], "clean_accuracy": test["accuracy"],
                                      "clean_count": test["count"], "official": official, "model_sha256": manifest["sha256"]}
    write_json(output / "provenance.json", audit)
    write_json(output / "evaluation.json", evaluation)
    (output / ".nojekyll").touch()
    files = {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()}
    zip_path = output.parent / (NAME + ".zip")
    if zip_path.exists():
        raise FileExistsError("Preserve existing submission archive")
    with zipfile.ZipFile(zip_path, "x", zipfile.ZIP_DEFLATED) as bundle:
        for name in files:
            bundle.write(output / name, name)
    if any(digest(ROOT / name) != value for name,value in preserved.items()):
        raise ValueError("Active assets changed during build")
    report = {"status": "PASS", "name": NAME, "built_utc": datetime.now(timezone.utc).isoformat(),
              "output": str(output), "archive": str(zip_path), "archive_sha256": digest(zip_path), "files_sha256": files,
              "provenance": audit, "active_assets_preserved": preserved,
              "excluded": ["pretrained digit readers", "pretrained word readers", "external model runtimes", "ROMs", "credentials", "datasets", "training checkpoints"],
              "browser_qa": "NOT RUN", "official_evaluation": "NOT RUN", "deployment": "NOT RUN"}
    destination = ROOT / "reports" / (NAME + "-build.json")
    if destination.exists():
        raise FileExistsError("Preserve existing build receipt")
    write_json(destination, report)
    print("PASS: four locally trained models, verified ancestry/exports; separate site and ZIP:", zip_path)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.output)
