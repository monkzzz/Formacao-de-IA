import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from digitlab import browser_ci


class BrowserCiTests(unittest.TestCase):
    def test_clean_checkout_preparation_restores_only_matching_missing_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "dist/model"
            folder.mkdir(parents=True)
            data = b"reviewed fixture"
            manifest = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            original = json.dumps(manifest)
            (folder / "manifest.json").write_text(original)
            payloads = {"model/weights.bin": data,
                        "model/parity.json": json.dumps({"model_sha256": manifest["sha256"]}).encode()}
            with patch.object(browser_ci, "MODELS", {"fixture": "model"}):
                self.assertEqual(browser_ci.prepare_weights(payloads, root), ["model/weights.bin", "model/parity.json"])
                self.assertEqual(browser_ci.prepare_weights(payloads, root), [])
                (folder / "weights.bin").write_bytes(b"different preserved weights")
                with self.assertRaises(ValueError):
                    browser_ci.prepare_weights(payloads, root)
                self.assertEqual((folder / "weights.bin").read_bytes(), b"different preserved weights")
            self.assertEqual((folder / "manifest.json").read_text(), original)

    def test_wrong_release_is_refused_before_writing_weights(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "dist/model"
            folder.mkdir(parents=True)
            (folder / "manifest.json").write_text(json.dumps({"sha256": "different", "bytes": 1}))
            with patch.object(browser_ci, "MODELS", {"fixture": "model"}), self.assertRaises(ValueError):
                browser_ci.prepare_weights({"model/weights.bin": b"x"}, root)
            self.assertFalse((folder / "weights.bin").exists())
