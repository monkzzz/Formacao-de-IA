import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from digitlab import submission_artifacts


class SubmissionArtifactTests(unittest.TestCase):
    def test_foreign_absolute_receipts_resolve_in_relocated_artifact_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for recorded in ("C:\\old-checkout\\artifacts\\release\\site", "/missing-old-checkout/site"):
                build = {"name": "release", "output": recorded, "archive": recorded + ".zip"}
                site, archive = submission_artifacts.resolve_artifacts(build, artifact_root=root)
                self.assertEqual(site, root / "release/site")
                self.assertEqual(archive, root / "release/release.zip")

    def test_new_paths_are_relative_and_overrides_take_precedence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "artifacts/release/site"
            target.mkdir(parents=True)
            with patch.object(submission_artifacts, "ROOT", root):
                self.assertEqual(submission_artifacts.portable_path(target), "artifacts/release/site")
                build = {"name": "release", "output": "artifacts/release/site", "archive": "artifacts/release/release.zip"}
                site, archive = submission_artifacts.resolve_artifacts(build, archive=root / "reviewed.zip")
                self.assertEqual(site, target)
                self.assertEqual(archive, root / "reviewed.zip")

    def test_package_names_cannot_escape_artifact_root(self):
        with self.assertRaises(ValueError):
            submission_artifacts.resolve_artifacts({"name": "../escape", "output": "x", "archive": "y"})
