"""Verify ML prerequisites in an isolated venv and fresh disposable source layout.

No training, checkpoint selection or official challenge inference is performed.
Font files stay on this Windows host; only identities are recorded.
"""

import hashlib
import json
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dia2-local"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report_path = Path(__file__).with_name("ml-reproducibility-preflight.json")
    workspace = APP / ".tmp/repro-source-20261017"
    if report_path.exists() or workspace.exists():
        raise SystemExit("Preserve previous probe; select new report/workspace names")
    if sys.prefix == sys.base_prefix or "repro-clean-20261017" not in sys.prefix:
        raise SystemExit("Run with the isolated repro-clean-20261017 interpreter")
    target = workspace / "dia2-local"
    shutil.copytree(APP / "digitlab", target / "digitlab", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    data = workspace / "Dia2/Dataset-MNIST/data"
    data.mkdir(parents=True)
    for path in (ROOT / "Dia2/Dataset-MNIST/data").glob("*.gz"):
        shutil.copy2(path, data / path.name)
    baseline = target / "artifacts/captcha-v2/best.pt"
    baseline.parent.mkdir(parents=True)
    shutil.copy2(APP / "artifacts/captcha-v2/best.pt", baseline)
    # Import only the copied project code under this venv's installed dependencies.
    sys.path.insert(0, str(target))
    import numpy as np
    import torch
    from digitlab.captcha import TRAIN_FONTS
    from digitlab.data import load_partition, split_indices
    from digitlab.highres import EXTRA_FONTS, HighResCNN
    from digitlab.residual import ADDED_FONTS, DEV_FONTS, TEST_FONTS, ResidualCNN, make_raw

    historical = json.loads((APP / "reports/captcha-v3.json").read_text(encoding="utf-8"))
    record = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL",
              "scope": "Clean dependency install and isolated training/evaluation prerequisites; no full retraining",
              "venv": sys.prefix, "system_site_packages_disabled": "include-system-site-packages = false" in (Path(sys.prefix) / "pyvenv.cfg").read_text(),
              "environment": {name: version(name) for name in ["torch", "numpy", "Pillow", "playwright"]}}
    try:
        assert record["system_site_packages_disabled"]
        for name, digest in historical["source_sha256"].items():
            assert sha(target / "digitlab" / name) == digest
        assert sha(baseline) == historical["baseline_checkpoint_sha256"]
        baseline_model = HighResCNN()
        baseline_model.load_state_dict(torch.load(baseline, weights_only=True, map_location="cpu"))
        selected = APP / "artifacts/captcha-v3/best.pt"
        selected_model = ResidualCNN()
        selected_model.load_state_dict(torch.load(selected, weights_only=True, map_location="cpu"))
        images, labels = load_partition(data, True)
        test_images, test_labels = load_partition(data, False)
        train, validation = split_indices(labels)
        assert images.shape == (60000, 28, 28) and test_images.shape == (10000, 28, 28)
        assert not np.intersect1d(train, validation).size
        assert len(train) == 55000 and len(validation) == 5000
        font_hashes = {}
        expected_fonts = historical["font_sha256"] | historical["test_font_sha256"]
        for name, digest in expected_fonts.items():
            path = Path("C:/Windows/Fonts") / name
            assert sha(path) == digest, name
            font_hashes[name] = digest
        assert set(TRAIN_FONTS + EXTRA_FONTS + ADDED_FONTS + DEV_FONTS + TEST_FONTS) == set(font_hashes)
        x, y = make_raw(images, labels, train[:2], [Path("C:/Windows/Fonts") / TRAIN_FONTS[0]], 20, 17)
        assert tuple(x.shape) == (20, 1, 64, 64) and torch.isfinite(x).all()
        assert len(y) == 20
        cli = {}
        for module in ["digitlab.residual", "digitlab.residual_evaluate"]:
            result = subprocess.run([sys.executable, "-m", module, "--help"], cwd=target,
                                    capture_output=True, text=True, timeout=60)
            assert result.returncode == 0, module
            cli[module] = {"returncode": result.returncode, "stdout": result.stdout}
        assert not (target / "artifacts/captcha-v3").exists()
        assert not (target / "reports/captcha-v3.json").exists()
        install = json.loads((APP / ".tmp/repro-clean-20261017-install.json").read_text(encoding="utf-8"))
        record.update(status="PASS", clean_install_packages=[{"name": p["metadata"]["name"], "version": p["metadata"]["version"]} for p in install["install"]],
                      dataset_hashes={p.name: sha(p) for p in data.glob("*.gz")},
                      split={"train": len(train), "validation": len(validation), "test": len(test_labels),
                             "train_indices_sha256": hashlib.sha256(train.tobytes()).hexdigest(),
                             "validation_indices_sha256": hashlib.sha256(validation.tobytes()).hexdigest()},
                      baseline_checkpoint_sha256=sha(baseline), selected_checkpoint_sha256=sha(selected),
                      font_hashes=font_hashes, source_sha256=historical["source_sha256"],
                      independent_training_renderer_probe={"count": 20, "source": "training split only", "shape": list(x.shape)},
                      training_and_export_cli=cli,
                      limits=["Full 12-epoch retraining NOT RUN; exact trained-weight reproduction not claimed",
                              "Checkpoints restored from existing local ignored artifacts, not from a verified public archive",
                              "44 font identities verified on this Windows host; font redistribution/other-host availability not established",
                              "Run a new experiment only in a separate layout; original trainer guards completed output paths"])
    except Exception as error:
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        with report_path.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
    print("PASS: clean dependencies, IDX/split, baseline/selected checkpoints, 44 fonts and training CLI prerequisites")


if __name__ == "__main__":
    main()
