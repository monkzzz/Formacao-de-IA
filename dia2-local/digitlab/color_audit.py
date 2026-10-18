"""Reproduce saved counts and render a fixed cross-palette visual sample."""

import json
import os

import numpy as np
from PIL import Image

from .color_preprocess import prepare_color
from .color_study import DIRECTORY, NAME, REPORT, gates, metrics, verify
from .preprocess import prepare
from .preprocessing_study import digest
from .train import ROOT, write_json


def main():
    output = ROOT / "reports" / (NAME + "-validation.json")
    if output.exists():
        raise FileExistsError("Preserve completed audit")
    d = json.loads(REPORT.read_text())
    verify(d)
    records = json.loads((DIRECTORY / "records.json").read_text())
    tests = json.loads((ROOT / "reports" / (NAME + "-unit-tests.json")).read_text())
    browser = json.loads((ROOT / "reports" / (NAME + "-browser.json")).read_text())
    checks = {"frozen_sources_fonts_datasets_and_active_assets": True,
              "source_files_unchanged": all(digest(DIRECTORY / name) == value for name,value in d["evidence_sha256"].items()),
              "fixture_hashes": all(digest(DIRECTORY / "fixtures" / r["file"]) == r["sha256"] for r in records),
              "unit_suite": tests["status"] == "PASS",
              "browser_same_study": browser["status"] == "PASS" and browser["study_sha256"] == digest(REPORT),
              "gates_reproduced": gates(d["results"]["rgb"], d["results"]["current"]) == d["gates"],
              "selection_matches_gates": d["eligible"] == all(d["gates"].values()) and d["selected"] == ("rgb" if d["eligible"] else "current")}
    with np.load(DIRECTORY / "source-split.npz") as splits:
        validation = set(splits["validation"])
        checks["source_split_disjoint"] = not bool(set(splits["train"]) & validation)
        checks["handwritten_sources_validation_only"] = all(r["source_index"] in validation for r in records if not r["printed"])
    for group in ("legacy", "color"):
        rows = [r for r in records if r["group"] == group]
        counts = [sum(r["label"] == digit and r["printed"] == printed for r in rows) for digit in range(10) for printed in (False, True)]
        checks[group + "_balanced_classes_and_sources"] = set(counts) == ({60} if group == "legacy" else {30})
    with np.load(DIRECTORY / "scores.npz") as scores:
        for name in ("current", "rgb"):
            for group in ("raw", "clean"):
                actual = metrics(scores[name + "_" + group], scores[group + "_labels"], scores[name + "_" + group + "_rejected"])
                checks[name + "_" + group + "_metrics"] = actual == d["results"][name][group]
    report = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
              "tests_run": tests["tests_run"], "independent_human_readability_review": "NOT RUN",
              "official_and_reserved_evaluation": "NOT RUN", "active_app_replacement": "NOT RUN",
              "failed_gates": [k for k,v in d["gates"].items() if not v]}
    write_json(output, report)
    if report["status"] != "PASS":
        raise ValueError("Integrity audit failed")
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tmp/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    indices = [0, 11, 22, 33] + [1200 + p * 20 + s * 10 + (p * 3 + s) % 10 for p in range(3) for s in range(2)]
    figure, axes = plt.subplots(len(indices), 3, figsize=(9, 23))
    for row, index in enumerate(indices):
        rgba = np.asarray(Image.open(DIRECTORY / "fixtures" / records[index]["file"]).convert("RGBA"))
        axes[row, 0].imshow(rgba)
        axes[row, 0].set_title(f"{index}: label {records[index]['label']}; palette {records[index]['palette']}", fontsize=8)
        for col, preparation in ((1, prepare), (2, prepare_color)):
            try:
                axes[row, col].imshow(preparation(rgba, 64)[0], cmap="gray", vmin=0, vmax=1)
            except ValueError:
                axes[row, col].text(.15, .5, "REJECTED", color="red")
            axes[row, col].set_title("Current grayscale" if col == 1 else "Experimental RGB", fontsize=8)
        for axis in axes[row]:
            axis.axis("off")
    figure.tight_layout()
    path = ROOT / "reports/screenshots" / (NAME + "-inputs.png")
    figure.savefig(path, dpi=100)
    plt.close(figure)
    write_json(ROOT / "reports" / (NAME + "-visual-sample.json"), {"indices": indices, "selection": "Fixed class/source/palette spread, independent of errors", "human_review": "NOT RUN"})
    print("PASS:", len(checks), "integrity checks; fixed contact sheet:", path)


if __name__ == "__main__":
    main()
