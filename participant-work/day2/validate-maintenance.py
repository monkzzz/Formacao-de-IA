"""Validate this maintenance batch without training or challenge inference.

Use the existing GSS environment (Pillow and PyYAML).
"""

import ast
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import PIL
from PIL import Image, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    destination = Path(__file__).with_name("maintenance-validation.json")
    if destination.exists():
        raise SystemExit("Report exists; choose a new destination")
    directory = ROOT / "dia2-local/.tmp/maintenance-20261017"
    paths = sorted((directory / "generated").glob("*.png"))
    assert len(paths) == 10
    hashes = {}
    for index, path in enumerate(paths, 1):
        assert path.name == f"caso_{index:02d}.png"
        with Image.open(path) as image:
            assert image.format == "PNG" and image.size == (192, 192)
            image.verify()
        hashes[path.name] = sha(path)
        assert hashes[path.name] == sha(directory / "generated-repeat" / path.name)
    assert len(set(hashes.values())) == 10
    preserved = json.loads(Path(__file__).with_name("submission-challenge-integrity.json").read_text())
    for name, digest in preserved["historical_report_hashes"].items():
        assert sha(ROOT / "dia2-local/reports" / name) == digest
    for case in preserved["cases"]:
        assert sha(ROOT / "Dia2/Desafio" / case["file"]) == case["file_sha256"]
    workflows = {}
    for name in ["avaliar-desafio-avancado", "gerar-desafio-avancado"]:
        path = ROOT / ".github/workflows" / (name + ".yml")
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        assert data["permissions"] == {"contents": "read"}
        scripts = re.findall(r"python (Dia2/[^\s]+\.py)", path.read_text(encoding="utf-8"))
        assert scripts and all((ROOT / script).is_file() for script in scripts)
        workflows[name] = {"scripts_exist": scripts, "triggers": list(data["on"])}
        if name.startswith("avaliar"):
            assert set(data["on"]) == {"workflow_dispatch"}
            assert data["on"]["workflow_dispatch"]["inputs"]["url"]["required"] == "true"
            assert data["on"]["workflow_dispatch"]["inputs"]["confirm_followup"]["default"] == "false"
            upload = data["jobs"]["verificar"]["steps"][-1]
            assert upload["if"] == "always()"
        else:
            assert "git push" not in path.read_text(encoding="utf-8")
            assert "/tmp/desafio-avancado" in path.read_text(encoding="utf-8")
    documents = ["README.md", "TASKS.md", "DIA2-PROPOSTA.md", "Dia2-Answers/README.md",
                 "Dia2-Answers/Desafio/README.md", "Dia2-Answers/Exercise-03/README.md",
                 "Dia2-Answers/Exercise-03/Part-03-Website.md", "Dia2-Answers/Exercise-03/Part-04-Challenge.md",
                 "Dia2/Dataset-MNIST/README.md", "Dia2/Desafio/README.md", "dia2-local/README.md",
                 "dia2-local/SKILLS.md", "dia2-local/docs/hosting.md", "dia2-local/reports/README.md",
                 "participant-work/day2/submission-challenge-chain.md", "participant-work/day2/maintenance-next-ten.md"]
    links = 0
    for name in documents:
        path = ROOT / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "#", "mailto:")):
                continue
            resolved = (path.parent / unquote(target.split("#")[0]))
            assert resolved.resolve() == destination.resolve() or resolved.exists(), (name, target)
            links += 1
    for path in [ROOT / "Dia2/Desafio/avaliar_captcha_no_site.py",
                 ROOT / "Dia2/Desafio/gerar_desafio_avancado.py", ROOT / "Dia2/Desafio/test_automation.py",
                 Path(__file__), Path(__file__).with_name("verify-challenge-chain.py")]:
        ast.parse(path.read_text(encoding="utf-8"))
    smoke = json.loads(Path(__file__).with_name("maintenance-evaluator-smoke.json").read_text())
    failure = json.loads(Path(__file__).with_name("maintenance-evaluator-failure.json").read_text())
    assert smoke["status"] == "PASS" and len(smoke["raw"]["predictions"]) == 10
    assert failure["status"] == "FAIL" and "HTTP(S)" in failure["error"]
    report = {"executed_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS",
              "relative_links_checked": links, "workflow_checks": workflows,
              "generator": {"count": 10, "format": "PNG", "size": [192, 192],
                            "same_environment_repeat_hashes_match": True,
                            "pillow": subprocess.check_output([
                                str(ROOT / "dia2-local/.venv/Scripts/python.exe"),
                                "-c", "import PIL; print(PIL.__version__)"], text=True).strip(),
                            "validator_pillow": PIL.__version__,
                            "font_hashes": {name: sha(Path(ImageFont.truetype(name, 12).path))
                                            for name in ["DejaVuSans-Bold.ttf", "DejaVuSerif-BoldItalic.ttf"]},
                            "hashes": hashes},
              "official_images_and_historical_records_preserved": True,
              "evaluator_real_browser_nonchallenge_smoke": "PASS: ten MNIST fixture uploads",
              "evaluator_failure_contract": "PASS: nonzero exit and diagnostic JSON",
              "automation_unit_tests": {"observed_result": "PASS", "tests": 4,
                                         "initial_sandbox_attempt": "Three temporary-directory access errors; one test passed",
                                         "retry": "All four passed after reviewed escalation"},
              "limits": ["GitHub-hosted Actions execution NOT RUN; local workflow parsing and script checks only",
                         "No official challenge inference, retraining, deployment or teacher feedback",
                         "Generator determinism verified only with this Pillow/font environment"]}
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(f"PASS: {links} relative links, workflows, PNG generation, preserved evidence and collector reports")


if __name__ == "__main__":
    main()
