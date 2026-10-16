"""Score the pre-frozen diagnostic candidate from the single cached test run."""

import hashlib
import json
import numpy as np

from .ensemble_benchmark import NAME, summarize, mix_scores
from .train import ROOT, write_json


def main():
    target = ROOT / "reports/ensemble-v1-candidate-test.json"
    if target.exists():
        raise SystemExit("Preserve completed test analysis")
    freeze_path = ROOT / "reports/ensemble-v1-evaluation-freeze.json"
    freeze = json.loads(freeze_path.read_text())
    development_path = ROOT / "reports/ensemble-v1-development.json"
    assert hashlib.sha256(development_path.read_bytes()).hexdigest() == freeze["development_report_sha256"]
    selection = ROOT / "artifacts" / NAME / "selection.json"
    assert hashlib.sha256(selection.read_bytes()).hexdigest() == freeze["selection_sha256"]
    test = json.loads((ROOT / "reports/ensemble-v1-test.json").read_text())
    assert test["model_identities"] == freeze["model_identities"]
    with np.load(ROOT / "artifacts" / NAME / "test.npz") as cached:
        data = dict(cached)
    candidate = summarize(data, freeze["diagnostic_ensemble_weight"])
    baseline = summarize(data, 1)
    score = mix_scores(data["low"], data["high"], freeze["diagnostic_ensemble_weight"])
    rows = [{"expected": int(label), "baseline": int(b), "candidate": int(c)}
            for label, b, c in zip(data["labels"][:60], data["high"][:60].argmax(1), score[:60].argmax(1))]
    report = {"status": "PASS", "scope": "One frozen diagnostic ensemble, scored from the single untouched test cache; not used for model selection",
              "freeze_sha256": hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
              "model_identities": freeze["model_identities"], "candidate": candidate, "baseline": baseline,
              "deployment_ensemble_selected": freeze["ensemble_selected"], "fixture_predictions": rows}
    write_json(target, report)
    print(json.dumps({"candidate": candidate["overall"], "baseline": baseline["overall"],
                      "complementarity": candidate["complementarity"]}, indent=2))


if __name__ == "__main__":
    main()
