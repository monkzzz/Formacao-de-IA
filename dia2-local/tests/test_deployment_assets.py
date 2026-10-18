import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from digitlab import deployment_assets, ftp_deploy


class DeploymentAssetsTests(unittest.TestCase):
    def test_restore_rejects_corrupt_weights_before_creating_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "dist/model"
            folder.mkdir(parents=True)
            (root / "deployment-files.json").write_text(json.dumps({"schema": 1, "files": ["model/weights.bin"]}))
            (folder / "manifest.json").write_text(json.dumps({"bytes": 4, "sha256": hashlib.sha256(b"good").hexdigest()}))
            with patch.object(deployment_assets, "ROOT", root), patch.object(ftp_deploy, "ROOT", root), \
                    patch.object(deployment_assets, "download", return_value=b"evil"):
                with self.assertRaises(ValueError):
                    deployment_assets.restore_weights()
                self.assertFalse((folder / "weights.bin").exists())

    def test_reviewed_license_and_weights_restore_and_verify(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "dist/model"
            folder.mkdir(parents=True)
            (root / "dist/LICENSE.txt").write_bytes(b"license")
            (root / "deployment-files.json").write_text(json.dumps({"schema": 1, "files": ["LICENSE.txt", "model/weights.bin"]}))
            (folder / "manifest.json").write_text(json.dumps({"bytes": 4, "sha256": hashlib.sha256(b"good").hexdigest()}))
            payloads = {"model/weights.bin": b"good", "LICENSE.txt": b"license"}
            with patch.object(deployment_assets, "ROOT", root), patch.object(ftp_deploy, "ROOT", root), \
                    patch.object(deployment_assets, "download", side_effect=payloads.__getitem__):
                self.assertEqual(deployment_assets.restore_weights(), ["model/weights.bin"])
                self.assertEqual(len(deployment_assets.verify_http()), 2)
                payloads["LICENSE.txt"] = b"changed"
                with self.assertRaisesRegex(ValueError, "Public asset hash mismatch"):
                    deployment_assets.verify_http()

    def test_restore_rejects_traversal_before_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "deployment-files.json").write_text(json.dumps({"files": ["model/../../weights.bin"]}))
            with patch.object(deployment_assets, "ROOT", root), patch.object(deployment_assets, "download") as fetch:
                with self.assertRaises(ValueError):
                    deployment_assets.restore_weights()
                fetch.assert_not_called()
