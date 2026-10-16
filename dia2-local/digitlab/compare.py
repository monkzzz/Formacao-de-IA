"""Compare preserved predictions with the answer key only after recording.

Parse the generator's literal DIGITS assignment without importing or executing
the generator. Write a separate comparison; never alter the raw predictions.
"""

import ast
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import torch
from PIL import Image

from .model import DigitCNN
from .preprocess import prepare
from .train import ROOT, write_json


def main():
    reports = ROOT / "reports"
    raw_path = reports / "challenge-raw.json"
    comparison_path = reports / "challenge-comparison.json"
    if not raw_path.exists():
        raise SystemExit("Record and preserve raw predictions before inspecting the answer key.")
    if comparison_path.exists():
        raise SystemExit("The first comparison already exists; preserve it.")
    raw_bytes = raw_path.read_bytes()
    raw_hash = hashlib.sha256(raw_bytes).hexdigest()
    raw = json.loads(raw_bytes)
    source = ROOT.parent / "Dia2/Desafio/gerar_desafio_avancado.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    labels = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DIGITS" for t in node.targets):
            labels = ast.literal_eval(node.value)
    if labels is None or sorted(labels) != list(range(10)):
        raise SystemExit("Expected exactly one label per digit in the answer-key literal.")
    torch.set_num_threads(2)
    model = DigitCNN().eval()
    model.load_state_dict(torch.load(ROOT / "artifacts/best.pt", weights_only=True, map_location="cpu"))
    manifest = json.loads((ROOT / "dist/model/manifest.json").read_text(encoding="utf-8"))
    assert manifest["sha256"] == raw["model_sha256"]
    assert hashlib.sha256((ROOT / "dist/model/weights.bin").read_bytes()).hexdigest() == raw["model_sha256"]
    cases = []
    prepared_dir = reports / "challenge-inputs"
    prepared_dir.mkdir(exist_ok=True)
    for i, label in enumerate(labels):
        record = raw["predictions"][i]
        name = f"caso_{i + 1:02d}.png"
        assert record["file"] == name
        path = ROOT.parent / "Dia2/Desafio" / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["file_sha256"]
        image = np.asarray(Image.open(path).convert("RGBA"))
        prepared = prepare(image)
        input_error = float(np.max(np.abs(prepared.flatten() - record["input"])))
        assert input_error <= 1e-6
        with torch.no_grad():
            logits = model(torch.from_numpy(prepared[None]))[0]
            scores = logits.softmax(0).numpy()
        score_error = float(np.max(np.abs(scores - record["scores"])))
        logit_error = float(np.max(np.abs(logits.numpy() - record["logits"])))
        assert score_error <= 1e-5 and logit_error <= 1e-4
        assert int(logits.argmax()) == record["predicted"]
        Image.fromarray((prepared[0] * 255).round().astype(np.uint8)).resize(
            (280, 280), Image.Resampling.NEAREST).save(prepared_dir / name)
        cases.append({"file": name, "expected": label, "predicted": record["predicted"],
                      "correct": label == record["predicted"],
                      "predicted_class_score": record["scores"][record["predicted"]],
                      "expected_class_score": record["scores"][label], "scores": record["scores"],
                      "preprocessing_max_error": input_error, "score_max_error": score_error,
                      "logit_max_error": logit_error})
    correct = sum(case["correct"] for case in cases)
    comparison = {"compared_at": datetime.now(timezone.utc).isoformat(),
                  "raw_sha256": raw_hash, "model_sha256": raw["model_sha256"],
                  "answer_key_source": "course generator DIGITS literal, inspected after raw predictions were saved",
                  "answer_key_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                  "count": 10, "correct": correct, "accuracy": correct / 10,
                  "cases": cases,
                  "limitations": ["Local application, not GitHub Pages", "No teacher review yet",
                                  "Only ten challenge cases", "Softmax scores are not calibrated certainty",
                                  "Collection retry repaired only a blob-URL assertion; frozen inference unchanged"]}
    with comparison_path.open("x", encoding="utf-8") as handle:
        json.dump(comparison, handle, indent=2, allow_nan=False)
    assert raw_path.read_bytes() == raw_bytes
    print(json.dumps({"correct": correct, "total": 10, "cases": cases}, indent=2))


if __name__ == "__main__":
    main()
