"""Validate setup download integrity without making network requests."""

import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stderr
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "course_setup", Path(__file__).resolve().parents[2] / "setup_course.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupCourseTests(unittest.TestCase):
    def test_invalid_options_fail_before_installation_or_downloads(self):
        invalid_options = (
            ["--component", "day1", "--install", "--browser", "--fonts"],
            ["--component", "day1", "--install", "--confidence"],
            ["--confidence", "--fonts"],
            ["--browser", "--fonts"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "unused-runtime"
            for arguments in invalid_options:
                with self.subTest(arguments=arguments), \
                        patch.object(setup.sys, "version_info", (3, 12)), \
                        patch.object(setup.venv, "EnvBuilder") as builder, \
                        patch.object(setup.subprocess, "run") as run, \
                        patch.object(setup, "download_fonts") as fonts, \
                        redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit) as error:
                    setup.main(arguments + ["--venv", str(directory)])
                self.assertEqual(error.exception.code, 2)
                builder.assert_not_called()
                run.assert_not_called()
                fonts.assert_not_called()
                self.assertFalse(directory.exists())

    def test_installed_runtime_can_add_browser_without_reinstalling(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "runtime with spaces"
            python = directory / ("Scripts/python.exe" if setup.os.name == "nt" else "bin/python")
            python.parent.mkdir(parents=True)
            python.touch()
            with patch.object(setup.sys, "version_info", (3, 12)), \
                    patch.object(setup.venv, "EnvBuilder") as builder, \
                    patch.object(setup.subprocess, "run") as run:
                setup.main(["--browser", "--venv", str(directory)])
            builder.assert_not_called()
            run.assert_called_once_with(
                [str(python), "-m", "playwright", "install", "chromium"], check=True)

    def test_each_component_keeps_cpu_install_and_correct_requirements(self):
        configurations = (
            ("day1", [], "Dia1/Exercicios-GSS/requirements.txt"),
            ("day2", [], "dia2-local/requirements.txt"),
            ("day2", ["--confidence"], "dia2-local/requirements-confidence.txt"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            for component, extra, requirements in configurations:
                with self.subTest(component=component, extra=extra), \
                        patch.object(setup.sys, "version_info", (3, 12)), \
                        patch.object(setup.venv, "EnvBuilder") as builder, \
                        patch.object(setup.subprocess, "run") as run:
                    setup.main(["--component", component, "--install", "--venv", temporary] + extra)
                builder.return_value.create.assert_called_once_with(Path(temporary))
                commands = [call.args[0] for call in run.call_args_list]
                self.assertEqual(len(commands), 2)
                self.assertIn("torch==2.14.1", commands[0])
                self.assertIn("https://download.pytorch.org/whl/cpu", commands[0])
                self.assertEqual(commands[1][-2:], ["-r", str(setup.ROOT / requirements)])

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
