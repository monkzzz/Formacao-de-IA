"""Maintenance collectors must preserve reports and screenshots independently."""

from pathlib import Path
import json
import tempfile
import unittest

from digitlab.qa_outputs import qa_outputs, qa_report


class QaOutputTests(unittest.TestCase):
    def test_failure_saves_completed_checks_and_preserves_existing_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "failed.json"
            report = {"checks": {}}
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with qa_report(destination, report):
                    report["checks"]["upload"] = "PASS"
                    raise RuntimeError("injected failure")
            saved = json.loads(destination.read_text())
            self.assertEqual(saved["status"], "FAIL")
            self.assertEqual(saved["checks"], {"upload": "PASS"})
            self.assertEqual(saved["failure"]["type"], "RuntimeError")
            original = destination.read_bytes()
            with self.assertRaises(FileExistsError):
                with qa_report(destination, {}):
                    pass
            self.assertEqual(destination.read_bytes(), original)

    def test_existing_report_or_screenshot_is_preserved(self):
        for existing in ("reports/run.json", "reports/screenshots/run-mobile.png"):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / existing
                target.parent.mkdir(parents=True)
                target.write_bytes(b"preserved evidence")
                with self.assertRaises(FileExistsError):
                    qa_outputs("run.json", "run", root=root)
                self.assertEqual(target.read_bytes(), b"preserved evidence")

    def test_absolute_report_and_named_screenshots(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report, images = qa_outputs(root / "separate report/result.json", "run-v2", ("390",), root=root)
            self.assertEqual(report, root / "separate report/result.json")
            self.assertEqual(images, {"390": root / "reports/screenshots/run-v2-390.png"})
            self.assertFalse(report.exists())
            self.assertFalse(images["390"].exists())
            relative, _ = qa_outputs("reports/relative.json", "relative", root=root)
            self.assertEqual(relative, root / "reports/relative.json")

    def test_prefix_cannot_escape_screenshot_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            for prefix in ("../other", "nested/path", "", "C:\\other"):
                with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                    qa_outputs("run.json", prefix, root=temporary)


if __name__ == "__main__":
    unittest.main()
