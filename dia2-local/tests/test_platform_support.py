"""Exercise portable discovery and fail explicitly on ambiguous font identity."""

import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from digitlab.platform_support import font_root, launch_browser, resolve_fonts


class PlatformSupportTests(unittest.TestCase):
    def test_font_override_and_windows_default(self):
        with patch.dict(os.environ, {"DIGITLAB_FONT_ROOT": "/explicit/fonts"}):
            self.assertEqual(font_root(), Path("/explicit/fonts"))
        with patch("digitlab.platform_support.os", SimpleNamespace(
                name="nt", environ={"WINDIR": "D:/Windows"})):
            self.assertEqual(font_root(), Path("D:/Windows/Fonts"))

    def test_exact_font_names_are_found_recursively_without_substitution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "family").mkdir()
            font = root / "family/Example.ttf"
            font.write_bytes(b"font fixture")
            self.assertEqual(resolve_fonts(root, ["EXAMPLE.TTF"]), [font])
            with self.assertRaisesRegex(ValueError, "never silently substituted"):
                resolve_fonts(root, ["Different.ttf"])
            (root / "another").mkdir()
            (root / "another/Example.ttf").write_bytes(b"different font fixture")
            with self.assertRaisesRegex(ValueError, "found 2"):
                resolve_fonts(root, ["Example.ttf"])

    def test_explicit_browser_path_takes_precedence(self):
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "browser"
            executable.touch()
            playwright = Mock()
            with patch.dict(os.environ, {"DIGITLAB_BROWSER_EXECUTABLE": str(executable)}):
                launch_browser(playwright)
            playwright.chromium.launch.assert_called_once_with(
                executable_path=str(executable), headless=True)

    def test_browser_uses_playwright_when_no_system_browser_exists(self):
        playwright = Mock()
        with patch("digitlab.platform_support.os", SimpleNamespace(name="posix", environ={})), \
                patch("digitlab.platform_support.shutil.which", return_value=None):
            launch_browser(playwright)
        playwright.chromium.launch.assert_called_once_with(headless=True)


if __name__ == "__main__":
    unittest.main()
