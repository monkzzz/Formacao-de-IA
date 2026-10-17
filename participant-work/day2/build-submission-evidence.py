"""Index preserved training evidence without training or opening challenge inputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
APP = ROOT / "dia2-local"


def main():
    if (HERE / "submission-model-identity.json").exists():
        raise SystemExit("Preserve existing identity evidence; choose a new destination for a later run.")
    report = json.loads((APP / "reports/captcha-v3.json").read_text(encoding="utf-8"))
    manifest = json.loads((APP / "dist/model/captcha-v3/digits/manifest.json").read_text(encoding="utf-8"))
    paths = ["reports/captcha-v3.json", "reports/captcha-v3-development-selection.json",
             "docs/residual-training.md", "digitlab/residual.py", "digitlab/residual_evaluate.py",
             "digitlab/data.py", "digitlab/preprocess.py", "digitlab/highres.py",
             "dist/model/captcha-v3/digits/manifest.json", "requirements-lock.txt",
             "dist/model/captcha-v3/digits/weights.bin", "artifacts/captcha-v3/best.pt"]
    identities = []
    for relative in paths:
        path = APP / relative
        identities.append({"path": "dia2-local/" + relative, "exists": path.exists(),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None})
    assert identities[-2]["sha256"] == manifest["sha256"]
    selection = json.loads((APP / "reports/captcha-v3-development-selection.json").read_text())
    selected = selection["records"]["selection.json"]["record"]
    assert identities[-1]["sha256"] == selected["checkpoint_sha256"]
    analysis = {}
    for key in ("test", "raw_test"):
        metric = report[key]
        matrix = metric["confusion_matrix"]
        errors = sorted(({"actual": i, "predicted": j, "count": n}
                         for i, row in enumerate(matrix) for j, n in enumerate(row) if i != j and n),
                        key=lambda item: item["count"], reverse=True)
        analysis[key] = {"count": metric["count"], "correct": metric["correct"],
                         "accuracy": metric["accuracy"], "errors": metric["count"] - metric["correct"],
                         "largest_confusions": errors[:5]}
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "source_commit": subprocess.check_output(["rtk", "git", "rev-parse", "HEAD"], text=True).strip(),
              "selected_model": "captcha-v3 / residual64-16-32-128 / epoch 12",
              "model_sha256": manifest["sha256"], "checkpoint_sha256": selected["checkpoint_sha256"],
              "training_environment": report.get("environment"), "split": report.get("split"),
              "training_seed": report["policy"]["seed"], "split_seed": 20261016,
              "epochs_recorded": len(report["history"]), "metrics_and_error_analysis": analysis,
              "identities": identities,
              "limitations": ["Index and confusion analysis of historical results; no fresh accuracy evaluation",
                              "Checkpoint and weights exist locally and remain ignored by Git",
                              "Current UI release is v3.10.0; selected trained CNN originated in v3.7.0"]}
    (HERE / "submission-model-identity.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
