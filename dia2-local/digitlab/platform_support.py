"""Explicit cross-platform font and browser discovery without font substitution."""

import os
from pathlib import Path
import shutil


def font_root():
    configured = os.environ.get("DIGITLAB_FONT_ROOT")
    if configured:
        return Path(configured).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    return Path("/usr/share/fonts/truetype")


def resolve_fonts(root, names):
    """Find exact filenames recursively; never replace a historical font."""
    root = Path(root)
    available = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in (".ttf", ".ttc", ".otf"):
            available.setdefault(path.name.casefold(), []).append(path)
    result = []
    for name in names:
        direct = root / name
        matches = [direct] if direct.is_file() else available.get(name.casefold(), [])
        if len(matches) != 1:
            raise ValueError(
                f"Font {name!r}: expected one exact file under {root}, found {len(matches)}. "
                "Use --fonts or DIGITLAB_FONT_ROOT with the recorded licensed fonts. "
                "For a new portable experiment use confidence_broad and its open-font bundle; "
                "historical fonts are never silently substituted.")
        result.append(matches[0])
    return result


def launch_browser(playwright):
    """Prefer an explicit executable, installed Chromium/Edge, then Playwright."""
    configured = os.environ.get("DIGITLAB_BROWSER_EXECUTABLE")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_file():
            raise ValueError(f"Configured browser does not exist: {path}")
        return playwright.chromium.launch(executable_path=str(path), headless=True)
    candidates = [shutil.which(name) for name in
                  ("chromium", "chromium-browser", "microsoft-edge", "google-chrome")]
    if os.name == "nt":
        candidates += [str(Path(os.environ.get(key, fallback)) / suffix)
                       for key, fallback, suffix in (
                           ("PROGRAMFILES(X86)", "C:/Program Files (x86)", "Microsoft/Edge/Application/msedge.exe"),
                           ("PROGRAMFILES", "C:/Program Files", "Microsoft/Edge/Application/msedge.exe"))]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return playwright.chromium.launch(executable_path=str(candidate), headless=True)
    return playwright.chromium.launch(headless=True)
