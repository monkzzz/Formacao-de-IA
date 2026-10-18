"""Preflight maintained browser QA destinations before opening a browser."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def atomic_json(path, value):
    """Replace a report only after its complete new JSON is durable on disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="." + path.name + ".", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def qa_report(destination, report):
    """Reserve fresh evidence, retain completed checks on failure, and re-raise."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    report["status"] = "RUNNING"
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    try:
        yield report
    except BaseException as error:
        report.update(status="FAIL", failure={"type": type(error).__name__, "message": str(error)[:1000]})
        raise
    else:
        report["status"] = "PASS"
    finally:
        atomic_json(destination, report)


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
