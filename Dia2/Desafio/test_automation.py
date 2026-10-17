"""Integrity and failure-contract tests; never classify official challenge inputs."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluator = load("avaliar_captcha_no_site")
generator = load("gerar_desafio_avancado")


class AutomationTests(unittest.TestCase):
    def test_official_input_requires_explicit_followup(self):
        with self.assertRaisesRegex(ValueError, "followup"):
            evaluator.input_files(Path(__file__).parent, False)

    def test_generator_refuses_official_and_nonempty_destinations(self):
        with self.assertRaisesRegex(ValueError, "reservada"):
            generator.gerar(Path(__file__).parent)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "preserve.txt").write_text("original")
            with self.assertRaisesRegex(ValueError, "vazia"):
                generator.gerar(path)
            self.assertEqual((path / "preserve.txt").read_text(), "original")

    def test_failure_writes_diagnostic_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "result.json"
            arguments = ["--url", "invalid", "--input-dir", folder, "--output", str(output)]
            self.assertEqual(evaluator.main(arguments), 1)
            before = output.read_bytes()
            self.assertEqual(json.loads(before)["status"], "FAIL")
            self.assertIn("HTTP(S)", json.loads(before)["error"])
            with self.assertRaises(SystemExit) as error:
                evaluator.main(arguments)
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(output.read_bytes(), before)

    def test_raw_record_identity_scores_and_count(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.png"
            path.write_bytes(b"fixture bytes; no image inference in this unit test")
            record = {"file": path.name, "model_sha256": "fixture-model",
                      "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "scores": [1.0] + [0.0] * 9, "predicted": 0}
            evaluator.validate_predictions([record], [path], "fixture-model")
            for patch in [{"file_sha256": "wrong"}, {"model_sha256": "wrong"},
                          {"scores": [float("nan")] * 10}, {"scores": [0.0] * 10},
                          {"predicted": 1}, {"error": "broken image"}]:
                with self.subTest(patch=patch), self.assertRaises(ValueError):
                    evaluator.validate_predictions([dict(record, **patch)], [path], "fixture-model")
            with self.assertRaisesRegex(ValueError, "count"):
                evaluator.validate_predictions([], [path], "fixture-model")


if __name__ == "__main__":
    unittest.main()
