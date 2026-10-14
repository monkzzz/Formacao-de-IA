#!/usr/bin/env python3
"""Testa os dez PNGs avancados pelo upload real do Image-classifier-demo.

Uso: python Dia2/Desafio/avaliar_captcha_no_site.py
Dependencia: pip install playwright; python -m playwright install chromium
Nao treina nem modifica o modelo. Use apos congelar a versao da rede.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_SITE = "https://vcanonici.github.io/Image-classifier-demo/"
DIRECTORY = Path(__file__).resolve().parent / "Avancado"
# Somente para avaliacao do professor. Nao compartilhar labels antes das previsoes.
EXPECTED = (8, 3, 0, 6, 1, 9, 4, 2, 7, 5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = sorted(DIRECTORY.glob("caso_??.png"))
    if len(paths) != 10:
        raise RuntimeError(f"Encontrados {len(paths)} PNGs; esperados 10.")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(args.site, wait_until="networkidle", timeout=90_000)
            page.get_by_label("Carregar imagens de dígitos").set_input_files(
                [str(path) for path in paths]
            )
            page.wait_for_function(
                "document.querySelectorAll('.upload-result').length === 10",
                timeout=120_000,
            )
            actual = []
            for index, image_path in enumerate(paths):
                row = page.locator(".upload-result").nth(index)
                filename = row.locator(".upload-filename").inner_text()
                if filename != image_path.name:
                    raise RuntimeError(
                        f"Ordem incorreta no resultado {index}: {filename}"
                    )
                prediction = int(
                    row.locator(".upload-prediction strong").inner_text()
                )
                actual.append(prediction)
        finally:
            browser.close()

    entries = [
        {
            "image": path.name,
            "expected": expected,
            "predicted": predicted,
            "correct": expected == predicted,
        }
        for path, expected, predicted in zip(paths, EXPECTED, actual)
    ]
    report = {
        "site": args.site,
        "total": len(entries),
        "correct": sum(item["correct"] for item in entries),
        "entries": entries,
    }
    result = json.dumps(report, indent=2, ensure_ascii=False)
    print(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
