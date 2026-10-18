import ftplib
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

from digitlab import ftp_deploy


class MemoryFTP:
    def __init__(self, *, fail_upload=False, corrupt=False, refuse_rename=False):
        self.files = {"index.html": b"working site"}
        self.fail_upload, self.corrupt, self.refuse_rename = fail_upload, corrupt, refuse_rename
        self.renames = []

    def retrbinary(self, command, callback):
        name = command.removeprefix("RETR ")
        if name not in self.files:
            raise ftplib.error_perm("550 missing")
        callback(self.files[name])

    def storbinary(self, command, stream):
        name = command.removeprefix("STOR ")
        self.files[name] = b"broken" if self.corrupt else stream.read()
        if self.fail_upload:
            raise ConnectionError("interrupted")

    def rename(self, before, after):
        if self.refuse_rename:
            raise ftplib.error_perm("550 replacement unsupported")
        self.renames.append((before, after))
        self.files[after] = self.files.pop(before)

    def delete(self, name):
        self.files.pop(name, None)

    def nlst(self):
        return list(self.files)


class FtpStagingTests(unittest.TestCase):
    def test_connection_failure_persists_receipt_without_exception_secrets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "dist").mkdir()
            (root / "dist/index.html").write_text("site")
            manifest = root / "deployment-files.json"
            manifest.write_text(json.dumps({"schema": 1, "files": ["index.html"]}))
            (root / "ftp.local.json").write_text(json.dumps({"host": "example.invalid", "username": "placeholder", "password": "placeholder"}))
            with patch.object(ftp_deploy, "ROOT", root), \
                    patch.object(sys, "argv", ["ftp_deploy", "--upload", "--report", "failed.json"]), \
                    patch.object(ftp_deploy, "connect", side_effect=ConnectionError("sensitive-test-marker")):
                with self.assertRaises(SystemExit):
                    ftp_deploy.main()
            content = (root / "reports/failed.json").read_text()
            self.assertNotIn("sensitive-test-marker", content)
            result = json.loads(content)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["files"], [])

    def test_failed_or_corrupt_upload_and_refused_rename_preserve_working_file(self):
        for options in ({"fail_upload": True}, {"corrupt": True}, {"refuse_rename": True}):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / "dist/index.html"
                source.parent.mkdir()
                source.write_bytes(b"new site")
                client = MemoryFTP(**options)
                report, journal = {"files": []}, []
                with patch.object(ftp_deploy, "ROOT", root):
                    with self.assertRaises((ConnectionError, RuntimeError, ftplib.error_perm)):
                        ftp_deploy.upload_file(client, source, root / "backup", report,
                                               lambda: journal.append(json.loads(json.dumps(report))))
                self.assertEqual(client.files, {"index.html": b"working site"})
                self.assertEqual((root / "backup/index.html").read_bytes(), b"working site")
                self.assertEqual(report["files"], [])
                self.assertTrue(journal)

    def test_success_publishes_only_verified_temporary_file_and_records_progress(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "dist/index.html"
            source.parent.mkdir()
            source.write_bytes(b"new site")
            report, journal = {"files": []}, []
            client = MemoryFTP()
            with patch.object(ftp_deploy, "ROOT", root):
                ftp_deploy.upload_file(client, source, root / "backup", report,
                                       lambda: journal.append(report["current_file"]["phase"]))
            self.assertEqual(client.files, {"index.html": b"new site"})
            self.assertEqual(client.renames[0][1], "index.html")
            self.assertIn("PUBLISHING_VERIFIED_TEMPORARY", journal)
            self.assertEqual(journal[-1], "PUBLISHED_AND_VERIFIED")
            self.assertEqual(report["files"][0]["file"], "index.html")

    def test_allowlist_rejects_roms_traversal_and_unreviewed_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "dist").mkdir()
            (root / "dist/index.html").write_text("site")
            manifest = root / "manifest.json"
            with patch.object(ftp_deploy, "ROOT", root):
                for name in ("../secret.json", "rom.sfc", "parity.json", "ftp.local.json", "x.bin"):
                    manifest.write_text(json.dumps({"schema": 1, "files": [name]}))
                    with self.assertRaises(ValueError):
                        ftp_deploy.deployment_files(manifest)
                manifest.write_text(json.dumps({"schema": 1, "files": ["index.html"]}))
                with self.assertRaises(ValueError):
                    ftp_deploy.deployment_files(manifest, ["unreviewed.js"])
