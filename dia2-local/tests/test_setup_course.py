"""Validate setup download integrity without making network requests."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "course_setup", Path(__file__).resolve().parents[2] / "setup_course.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupCourseTests(unittest.TestCase):
    def test_existing_bundle_is_verified_offline_and_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "fonts"
            destination.mkdir()
            (destination / "font.ttf").write_bytes(b"recorded font fixture")
            checksum = hashlib.sha256((destination / "font.ttf").read_bytes()).hexdigest()
            manifest = {"sha256": {"font.ttf": checksum}, "groups": {"train": ["font.ttf"]}}
            (destination / "font-groups.json").write_text(json.dumps(manifest))
            docs = root / "dia2-local/docs"
            docs.mkdir(parents=True)
            (docs / "confidence-fonts.json").write_text(json.dumps(manifest))
            with patch.object(setup, "ROOT", root), patch.object(setup, "urlopen") as network:
                setup.download_fonts(destination)
                network.assert_not_called()
                (destination / "font.ttf").write_bytes(b"changed fixture")
                with self.assertRaisesRegex(ValueError, "Font bundle changed"):
                    setup.download_fonts(destination)

    def test_download_verifies_pinned_bytes_and_keeps_license(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "dia2-local/docs"
            docs.mkdir(parents=True)
            font = b"\x00\x01\x00\x00font fixture"
            license_text = b"license fixture"
            expected = {"sha256": {"example/Example.ttf": hashlib.sha256(font).hexdigest(),
                                    "example/OFL.txt": hashlib.sha256(license_text).hexdigest()}}
            (docs / "confidence-fonts.json").write_text(json.dumps(expected))
            def response(url, timeout):
                self.assertIn(setup.FONT_REVISION, url)
                return io.BytesIO(license_text if url.endswith("OFL.txt") else font)
            with patch.object(setup, "ROOT", root), \
                    patch.object(setup, "FONT_FILES", {"train": {"example": ["Example.ttf"]}}), \
                    patch.object(setup, "urlopen", side_effect=response):
                setup.download_fonts(root / "fonts")
            manifest = json.loads((root / "fonts/font-groups.json").read_text())
            self.assertEqual(manifest["licenses"], {"example": "example/OFL.txt"})
            self.assertEqual(manifest["sha256"], expected["sha256"])


if __name__ == "__main__":
    unittest.main()
