import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


class CollectorFailureTests(unittest.TestCase):
    def test_maintained_collectors_keep_browser_start_failures(self):
        for name in ("design_qa", "helper_qa", "words_qa", "digit_readers_qa", "selectable_models_qa"):
            with self.subTest(collector=name), tempfile.TemporaryDirectory() as temporary:
                module = importlib.import_module("digitlab." + name)
                root = Path(temporary)
                arguments = [name]
                if name == "helper_qa":
                    arguments += ["--report-prefix", "failure"]
                    target = root / "reports/failure-qa.json"
                else:
                    target = root / "reports/failure.json"
                    arguments += ["--report", str(target), "--screenshot-prefix", "failure"]
                if name == "selectable_models_qa":
                    for folder in ("model", "model/mnist-supplementary-v1/digits", "model/captcha-v3/digits"):
                        path = root / "dist" / folder / "manifest.json"
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("{}")
                    fixtures = root / "artifacts/mnist-supplementary-v1/fixtures"
                    fixtures.mkdir(parents=True)
                    for i in range(10):
                        (fixtures / f"sample-{i}.png").write_bytes(b"unused; launch fails first")
                with patch("digitlab.qa_outputs.ROOT", root), patch.object(sys, "argv", arguments), \
                        patch.object(module, "sync_playwright", side_effect=RuntimeError("injected browser failure")), \
                        patch.object(module, "ROOT", root if name == "selectable_models_qa" else module.ROOT):
                    with self.assertRaisesRegex(RuntimeError, "injected browser failure"):
                        module.main()
                saved = json.loads(target.read_text())
                self.assertEqual(saved["status"], "FAIL")
                self.assertEqual(saved["failure"]["type"], "RuntimeError")
