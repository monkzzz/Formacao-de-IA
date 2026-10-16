"""One final follow-up challenge evaluation, preserving the historical first run.

Never use this result to select weights or adjust inference. Existing challenge
answers are public in this project, so this is not a new blind evaluation.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from .qa import open_browser
from .train import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8766/")
    args = parser.parse_args()
    reports = ROOT / "reports"
    freeze_path = reports / "robust-challenge-freeze.json"
    raw_path = reports / "robust-challenge-raw.json"
    comparison_path = reports / "robust-challenge-comparison.json"
    if any(path.exists() for path in [freeze_path, raw_path, comparison_path]):
        raise SystemExit("Follow-up evaluation already started. Preserve its records.")
    qa = json.loads((reports / "robust-browser-qa.json").read_text(encoding="utf-8"))
    assert qa["status"] == "PASS"
    manifest = json.loads((ROOT / "dist/model/robust/digits/manifest.json").read_text(encoding="utf-8"))
    sources = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
        for path in sorted([*ROOT.glob("digitlab/*.py"), *ROOT.glob("dist/v3/*.js"),
            ROOT / "dist/index.html", ROOT / "dist/model/robust/digits/manifest.json",
            ROOT / "dist/model/robust/digits/weights.bin"])}
    create_json(freeze_path, {"frozen_at": datetime.now(timezone.utc).isoformat(),
        "model_sha256": manifest["sha256"], "sources": sources,
        "selection": "Clean and synthetic noisy validation only; no challenge input",
        "scope": "Follow-up evaluation; original answers/results were already available, not blind",
        "further_tuning_permitted": False})
    # Freeze runtime and selected weights before loading any official images.
    directory = ROOT.parent / "Dia2/Desafio"
    paths = [directory / f"caso_{i:02d}.png" for i in range(1, 11)]
    with sync_playwright() as playwright:
        browser = open_browser(playwright)
        page = browser.new_page()
        page.goto(args.url)
        page.wait_for_function("window.digitLab?.state.ready", timeout=60000)
        assert page.evaluate("digitLab.state.model.manifest.sha256") == manifest["sha256"]
        page.locator("#files").set_input_files([str(path) for path in paths])
        page.wait_for_function("digitLab.state.uploads.length === 10 && !digitLab.state.busy", timeout=60000)
        raw = page.evaluate("digitLab.exportRecord()")
        assert [row["file"] for row in raw["predictions"]] == [path.name for path in paths]
        assert all("error" not in row and row["model_sha256"] == manifest["sha256"] for row in raw["predictions"])
        raw["freeze_sha256"] = digest(freeze_path)
        raw["input_sha256"] = {path.name: digest(path) for path in paths}
        raw["evaluation_scope"] = "Follow-up final evaluation, not a new blind first run"
        create_json(raw_path, raw)
        page.screenshot(path=str(reports / "screenshots/robust-challenge.png"), full_page=True)
        browser.close()
    assert all(digest(ROOT / name) == value for name, value in sources.items())
    # Durable predictions are saved before reading the historical answer key.
    original = json.loads((reports / "challenge-comparison.json").read_text(encoding="utf-8"))
    expected = {row["file"]: row["expected"] for row in original["cases"]}
    cases = [{"file": row["file"], "expected": expected[row["file"]],
        "predicted": int(row["predicted"]), "correct": int(row["predicted"]) == expected[row["file"]]}
        for row in raw["predictions"]]
    correct = sum(row["correct"] for row in cases)
    create_json(comparison_path, {"model_sha256": manifest["sha256"], "raw_sha256": digest(raw_path),
        "scope": raw["evaluation_scope"], "count": 10, "correct": correct, "accuracy": correct / 10,
        "original_correct": original["correct"], "answer_key_source": "Historical challenge-comparison.json",
        "cases": cases})
    print(f"Final follow-up challenge: {correct}/10; original {original['correct']}/10. No further tuning.")


if __name__ == "__main__":
    main()
