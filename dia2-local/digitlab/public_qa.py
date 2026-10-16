"""Run the existing browser checks publicly while preserving local evidence."""

import shutil
import sys
import argparse

from . import qa
from .train import ROOT, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://naoquerosaber.pt/AI/")
    parser.add_argument("--report", help="Separate JSON report filename for a later interface release")
    args = parser.parse_args()
    local = args.url.startswith("http://127.0.0.1:")
    report_name = "digits-browser-qa-v2.json" if local else "public-browser-qa-v2.json"
    prefix = "digits-v2-" if local else "public-digits-v2-"
    if args.report:
        if "/" in args.report or "\\" in args.report or not args.report.endswith(".json"):
            parser.error("--report must be a JSON filename")
        report_name = args.report
        prefix = args.report.removesuffix(".json") + "-"
    saved = ROOT / "artifacts/local-qa-screenshots"
    saved.mkdir(exist_ok=True)
    screenshots = ROOT / "reports/screenshots"
    names = ["desktop.png", "mobile.png"]
    for name in names:
        if (screenshots / name).exists():
            shutil.copy2(screenshots / name, saved / name)
    # Preserve the original, frozen-source QA implementation and its local report.
    qa.write_json = lambda path, value: write_json(ROOT / "reports" / report_name, value)
    sys.argv = [sys.argv[0], "--url", args.url]
    try:
        qa.main()
        for name in names:
            shutil.copy2(screenshots / name, screenshots / (prefix + name))
    finally:
        for name in names:
            if (saved / name).exists():
                shutil.copy2(saved / name, screenshots / name)
    print("Digit regression checks saved separately in reports/" + report_name)


if __name__ == "__main__":
    main()
