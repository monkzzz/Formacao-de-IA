"""Resolve new portable receipts and relocate historical Windows/Linux artifacts."""

from pathlib import Path
import re

from .train import ROOT


def portable_path(path):
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_artifacts(build, *, site=None, archive=None, artifact_root=None):
    name = build["name"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", name):
        raise ValueError("Unsafe package identity")
    root = Path(artifact_root) if artifact_root is not None else ROOT / "artifacts"
    def resolve(override, recorded, fallback):
        if override is not None:
            return Path(override).resolve()
        if artifact_root is None:
            previous = Path(recorded)
            previous = previous if previous.is_absolute() else ROOT / previous
            if previous.exists():
                return previous.resolve()
        return (root / name / fallback).resolve()
    return (resolve(site, build["output"], "site"),
            resolve(archive, build["archive"], name + ".zip"))
