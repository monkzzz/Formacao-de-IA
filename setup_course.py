"""Prepare isolated course runtimes on Windows or Linux (Python 3.12+)."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote
from urllib.request import urlopen
import venv

ROOT = Path(__file__).resolve().parent
FONT_REVISION = "47d54ca1ebb14fd864695f1d39dc734f39017c33"
FONT_FILES = {
    "train": {
        "notosans": ["NotoSans[wdth,wght].ttf", "NotoSans-Italic[wdth,wght].ttf"],
        "notoserif": ["NotoSerif[wdth,wght].ttf", "NotoSerif-Italic[wdth,wght].ttf"],
        "robotoslab": ["RobotoSlab[wght].ttf"], "oswald": ["Oswald[wght].ttf"],
    },
    "development": {"lato": ["Lato-Regular.ttf", "Lato-Bold.ttf", "Lato-Italic.ttf", "Lato-BoldItalic.ttf"]},
    "test": {"ubuntu": ["Ubuntu-Regular.ttf", "Ubuntu-Bold.ttf", "Ubuntu-Italic.ttf", "Ubuntu-BoldItalic.ttf"]},
}


def download_fonts(destination):
    """Fetch open fonts and licenses; preserve every existing file and manifest."""
    manifest_path = destination / "font-groups.json"
    expected = json.loads((ROOT / "dia2-local/docs/confidence-fonts.json").read_text())
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest["sha256"] != expected["sha256"] or manifest["groups"] != expected["groups"]:
            raise ValueError("Existing bundle differs from the pinned font manifest")
        for name, checksum in manifest["sha256"].items():
            if hashlib.sha256((destination / name).read_bytes()).hexdigest() != checksum:
                raise ValueError(f"Font bundle changed: {name}")
        print(f"Verified existing font bundle: {destination}")
        return
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {"groups": {}, "sha256": {}, "sources": {}, "licenses": {}}
    for group, families in FONT_FILES.items():
        manifest["groups"][group] = []
        for family, names in families.items():
            license_name = {"ubuntu": "UFL.txt", "robotoslab": "LICENSE.txt"}.get(family, "OFL.txt")
            collection = {"ubuntu": "ufl", "robotoslab": "apache"}.get(family, "ofl")
            for name in names + [license_name]:
                relative = family + "/" + name
                url = "https://raw.githubusercontent.com/google/fonts/" + FONT_REVISION + "/" + collection + "/" + quote(relative)
                path = destination / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    print(f"Downloading {relative}", flush=True)
                    with urlopen(url, timeout=60) as response:
                        data = response.read()
                    # Prevent saving an error page as a usable font.
                    if name.endswith(".ttf") and data[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"ttcf"):
                        raise ValueError(f"Invalid font download: {relative}")
                    with path.open("xb") as stream:
                        stream.write(data)
                checksum = hashlib.sha256(path.read_bytes()).hexdigest()
                if checksum != expected["sha256"][relative]:
                    raise ValueError(f"Download differs from pinned font manifest: {relative}")
                manifest["sha256"][relative] = checksum
                manifest["sources"][relative] = url
                if name == license_name:
                    manifest["licenses"][family] = relative
                else:
                    manifest["groups"][group].append(relative)
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
    print(f"Prepared font bundle with licenses and hashes: {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=("day1", "day2"), default="day2")
    parser.add_argument("--install", action="store_true", help="Create a venv and install component requirements")
    parser.add_argument("--browser", action="store_true", help="Install Playwright Chromium for Day 2")
    parser.add_argument("--confidence", action="store_true", help="Include Day 2 confidence-suite plotting dependencies")
    parser.add_argument("--fonts", action="store_true", help="Download the open-font confidence-experiment bundle")
    parser.add_argument("--venv", type=Path, help="Override the platform-specific environment directory")
    args = parser.parse_args()
    if args.confidence and (args.component != "day2" or not args.install):
        parser.error("--confidence requires --component day2 --install")
    if sys.version_info < (3, 12):
        parser.error("Use Python 3.12 or later")
    directory = args.venv or ROOT / ".runtime" / ("windows" if os.name == "nt" else "linux") / args.component
    python = directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if args.install:
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(directory)
        requirements = ROOT / ("Dia1/Exercicios-GSS/requirements.txt" if args.component == "day1" else "dia2-local/requirements.txt")
        if args.confidence:
            requirements = ROOT / "dia2-local/requirements-confidence.txt"
        command = [str(python), "-m", "pip", "install", "-r", str(requirements)]
        # The course uses CPU training; avoid downloading unnecessary CUDA packages.
        if args.component in ("day1", "day2"):
            subprocess.run([str(python), "-m", "pip", "install", "torch==2.14.1", "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
        subprocess.run(command, check=True)
    if args.browser:
        if args.component != "day2" or not python.exists():
            parser.error("--browser requires an installed Day 2 environment")
        subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)
    if args.fonts:
        download_fonts(ROOT / "dia2-local/data/open-fonts")
    print(f"Runtime Python: {python}")
    print("Run commands with that Python directly; shell activation is optional.")


if __name__ == "__main__":
    main()
