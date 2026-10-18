"""Preflight maintained browser QA destinations before opening a browser."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def qa_outputs(report, prefix, names=("desktop", "mobile"), *, root=None):
    """Return new report/screenshot paths; reject collisions and unsafe prefixes."""
    root = Path(root) if root is not None else ROOT
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", prefix):
        raise ValueError("Use a filename prefix, without directories, for QA screenshots")
    report = Path(report)
    if not report.is_absolute():
        report = root / report if report.parts[0] == "reports" else root / "reports" / report
    screenshots = {name: root / "reports/screenshots" / f"{prefix}-{name}.png" for name in names}
    for path in (report, *screenshots.values()):
        if path.exists():
            raise FileExistsError(f"Preserve existing QA evidence; choose a new destination: {path}")
    report.parent.mkdir(parents=True, exist_ok=True)
    (root / "reports/screenshots").mkdir(parents=True, exist_ok=True)
    return report, screenshots
