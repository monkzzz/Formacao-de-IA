"""Check preserved evidence bytes and recorded outputs; no inference or tuning."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dia2-local"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((APP / "reports" / name).read_text(encoding="utf-8"))


def main():
    destination = Path(__file__).with_name("submission-challenge-integrity.json")
    if destination.exists():
        raise SystemExit("Evidence exists; select a new report destination")
    raw_name = "captcha-v3-challenge-raw.json"
    public_name = "release-3.7.0-public-challenge-verification-raw.json"
    raw, public = read(raw_name), read(public_name)
    freeze = read("captcha-v3-challenge-freeze.json")
    comparison = read("captcha-v3-challenge-comparison.json")
    verification = read("release-3.7.0-public-challenge-verification.json")
    assert sha(APP / "reports" / raw_name) == comparison["raw_sha256"]
    assert sha(APP / "reports" / public_name) == verification["raw_sha256"]
    assert raw["model_sha256"] == public["model_sha256"] == freeze["model_sha256"] == comparison["model_sha256"]
    assert len(raw["predictions"]) == len(public["predictions"]) == 10
    originals = read("challenge-freeze.json")
    assert sha(APP / "artifacts/frozen-app.zip") == originals["archive_sha256"]
    assert sha(APP / "dist/model/weights.bin") == originals["model_sha256"]
    unchanged_runtime = {}
    for name in ["dist/v3/inference.js", "dist/v3/preprocess.js", "dist/v3/residual.js",
                 "dist/model/captcha-v3/digits/manifest.json", "dist/model/captcha-v3/digits/weights.bin"]:
        unchanged_runtime[name] = sha(APP / name)
        assert unchanged_runtime[name] == freeze["sources"][name], name
    cases = []
    for index, (local, deployed, result) in enumerate(zip(raw["predictions"], public["predictions"], comparison["cases"]), 1):
        name = f"caso_{index:02d}.png"
        assert local["file"] == deployed["file"] == result["file"] == name
        assert local["file_sha256"] == deployed["file_sha256"] == sha(ROOT / "Dia2/Desafio" / name)
        assert len(local["scores"]) == 10 and local["input"] == deployed["input"]
        assert local["scores"] == deployed["scores"]
        assert local["predicted"] == deployed["predicted"] == result["predicted"]
        assert result["correct"] == (result["predicted"] == result["expected"])
        cases.append({"file": name, "file_sha256": local["file_sha256"], "predicted": local["predicted"],
                      "correct": result["correct"], "scores_and_inputs_match_public_record": True})
    assert sum(item["correct"] for item in cases) == comparison["correct"] == 10
    names = ["challenge-freeze.json", "challenge-raw.json", "challenge-comparison.json",
             "captcha-v3-challenge-freeze.json", raw_name, "captcha-v3-challenge-comparison.json",
             public_name, "release-3.7.0-public-challenge-verification.json"]
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "scope": "Existing evidence integrity only; no new challenge inference",
              "cases": cases, "historical_report_hashes": {name: sha(APP / "reports" / name) for name in names},
              "unchanged_selected_runtime": unchanged_runtime,
              "original_frozen_archive_sha256": originals["archive_sha256"],
              "current_origin_retest": "NOT RUN: same origin and default model; preserved results used",
              "limits": ["Entry page and UI changed since v3.7.0; only listed runtime files matched",
                         "Hash verification does not prove every historical process claim",
                         "Known ten-image follow-up; not independent population accuracy"]}
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("PASS: preserved challenge chain, ten recorded outputs and unchanged CNN runtime")


if __name__ == "__main__":
    main()
