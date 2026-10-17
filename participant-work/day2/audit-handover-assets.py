"""Inventory remaining local files, teaching assets and preserved handover evidence.

Requires PyMuPDF in the ignored handover-pdf-deps directory and Pillow/PyYAML
from the existing GSS environment. No inference, training or external messages.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw
import yaml

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dia2-local"
sys.path.insert(0, str(APP / ".tmp/handover-pdf-deps"))
import pymupdf


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    destination = Path(__file__).with_name("handover-asset-audit.json")
    if destination.exists():
        raise SystemExit("Report exists; choose a new destination")
    output = APP / ".tmp/handover-assets"
    output.mkdir(parents=True, exist_ok=True)
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "scope": "Local inventory and integrity review; no rights clearance or human feedback"}
    image_decisions = []
    for source, target in [("65474617.jpg", "dist/assets/65474617.jpg"),
                           ("scopedog-asset.jpg", "dist/assets/scopedog.jpg")]:
        assert sha(APP / source) == sha(APP / target)
        with Image.open(APP / source) as image:
            image_decisions.append({"path": source, "bytes": (APP / source).stat().st_size,
                                    "size": list(image.size), "sha256": sha(APP / source),
                                    "duplicate_of": target, "decision": "Keep local, ignore exact duplicate; tracked serving asset retained"})
    report["duplicate_images"] = image_decisions
    records = []
    for raw_name, comparison_name, baseline in [
        ("ensemble-v1-post-publication-challenge-verification-raw.json",
         "ensemble-v1-post-publication-challenge-verification.json", "captcha-v2-challenge-raw.json"),
        ("release-3.7.0-public-challenge-recheck-20261016-raw.json",
         "release-3.7.0-public-challenge-recheck-20261016.json", "captcha-v3-challenge-raw.json")]:
        raw, comparison, original = [read(APP / "reports" / name) for name in [raw_name, comparison_name, baseline]]
        assert sha(APP / "reports" / raw_name) == comparison["raw_sha256"]
        assert raw["model_sha256"] == comparison["model_sha256"] == original["model_sha256"]
        assert len(raw["predictions"]) == len(comparison["cases"]) == 10
        for actual, frozen, result in zip(raw["predictions"], original["predictions"], comparison["cases"]):
            assert actual["file"] == frozen["file"] == result["file"]
            assert actual["file_sha256"] == sha(ROOT / "Dia2/Desafio" / actual["file"])
            assert actual["input"] == frozen["input"] and actual["scores"] == frozen["scores"]
            assert actual["predicted"] == frozen["predicted"] == result["predicted"]
        assert sum(c["correct"] for c in comparison["cases"]) == comparison["correct"]
        records.append({"raw": raw_name, "comparison": comparison_name, "baseline": baseline,
                        "raw_sha256": comparison["raw_sha256"], "comparison_sha256": sha(APP / "reports" / comparison_name),
                        "count": 10, "correct": comparison["correct"],
                        "decision": "Commit unchanged historical follow-up evidence; not a new accuracy test"})
    report["historical_followups"] = records
    provenance = read(ROOT / "Dia1/Exercicios-GSS/origem.json")
    for entry in provenance["ficheiros"]:
        assert sha(ROOT / "Dia1/Exercicios-GSS" / entry["destino"]) == entry["sha256_destino"]
    report["gss_provenance"] = {"repository": provenance["repositorio"], "commit": provenance["commit"],
                                "files_verified": len(provenance["ficheiros"]),
                                "recorded_adaptations": sum(x["sha256_origem"] != x["sha256_destino"] for x in provenance["ficheiros"]),
                                "manifest_sha256": sha(ROOT / "Dia1/Exercicios-GSS/origem.json")}
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert citation["license"] == "CC-BY-4.0"
    assert [a["family-names"] for a in citation["authors"]] == ["Canonici", "Gomes"]
    license_text = (ROOT / "LICENSE.md").read_text(encoding="utf-8")
    assert "Vinicius Canonici e Hugo Gomes" in license_text and "CC BY 4.0" in license_text
    report["license_citation_consistency"] = {"authors_and_license_match": True,
                                               "upstream_repository_metadata_retained": citation["repository-code"]}
    slides = []
    sheet = Image.new("RGB", (1500, 4 * 280), "white")
    draw = ImageDraw.Draw(sheet)
    expected = {"Whoami": 27, "The Basics": 48, "LLM Anatomy": 83,
                "From LLM to Chatbot": 33, "Context Eng": 49, "Model Chosing": 19,
                "Coding Agents": 38, "Agentic Context Eng": 44, "Task eng": 34, "VDD and Autonomy": 21}
    for day in ["Dia1", "Dia2"]:
        for path in sorted((ROOT / day / "Teorico").glob("*.pdf")):
            with pymupdf.open(path) as pdf:
                assert len(pdf) == expected.get(path.stem, 83)
                assert path.stat().st_size < 20_000_000
                index = len(slides)
                pixmap = pdf[0].get_pixmap(matrix=pymupdf.Matrix(.45, .45))
                cover = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                cover.thumbnail((485, 240))
                x, y = (index % 3) * 500, (index // 3) * 280
                sheet.paste(cover, (x, y + 25))
                draw.text((x + 4, y + 4), f"{day}: {path.stem[:45]} ({len(pdf)} pages)", fill="black")
                if path.stem == "LLM Anatomy":
                    pdf[17].get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(str(output / "llm-anatomy-page-18.png"))
                if path.stem == "From LLM to Chatbot":
                    pdf[26].get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(str(output / "chatbot-page-27.png"))
                slides.append({"file": path.relative_to(ROOT).as_posix(), "pages": len(pdf),
                               "bytes": path.stat().st_size, "sha256": sha(path),
                               "first_page_text_characters": len(pdf[0].get_text().strip())})
    assert len(slides) == 11 and sum(item["pages"] for item in slides) == 479
    sheet.save(output / "slide-covers.png")
    report["slides"] = slides
    report["pdf_review_method"] = "Fresh metadata/cover renders and two targeted pages; earlier full contact-sheet review remains in SLIDE-REVIEW.md"
    generic = read(Path(__file__).with_name("starter-generic-1.0.0.json"))
    assert sha(Path(__file__).with_name(generic["archive"])) == generic["archive_sha256"]
    original = read(ROOT / "participant-work/day1/synthesis-preservation.json")
    assert sha(ROOT / "participant-work/day1" / original["path"]) == original["sha256"]
    context = read(Path(__file__).with_name("bootstrap-context-version.json"))
    for name, digest in context["files"].items():
        assert sha(ROOT / name) == digest
    report["preservation"] = {"generic_starter_archive_matches": True, "original_synthesis_matches": True,
                               "recorded_skill_and_context_files_match_before_handoff_update": True}
    report["tooling"] = {"pdf": pymupdf.__version__, "initial_pdf_install": "Restricted attempt failed; reviewed escalation succeeded into ignored target",
                         "restricted_audit": "Package directory access prevented import; reviewed escalation used",
                         "page_total_correction": "Initial aggregate assertion used the previous incorrect 579-page total; individual deck counts matched. Correct total is 479."}
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print("PASS: five remaining untracked files reviewed, 63 provenance hashes and 11 decks/479 pages verified")


if __name__ == "__main__":
    main()
