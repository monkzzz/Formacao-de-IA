#!/usr/bin/env python3
"""Gera dez digitos CAPTCHA para estudo de robustez da classificacao MNIST.

Distorcoes de forma, quebras reais nos tracos, oclusoes, ruido estruturado e
linhas interferentes. Os nomes dos arquivos nao contem a classe.
Uso: python Dia2/Desafio/gerar_desafio_avancado.py
Requer Pillow. Geracao deterministica, sem usar ou ajustar o classificador.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 192
FACTOR = 3
W = SIZE * FACTOR
OUTPUT = Path(__file__).resolve().parent / "Avancado"
DIGITS = (8, 3, 0, 6, 1, 9, 4, 2, 7, 5)
FONTS = ("DejaVuSans-Bold.ttf", "DejaVuSerif-BoldItalic.ttf")
INKS = (
    (34, 39, 81), (53, 41, 77), (38, 69, 65), (55, 50, 75), (32, 51, 91),
    (63, 39, 62), (43, 59, 65), (47, 45, 82), (45, 53, 66), (72, 52, 55),
)
PAPERS = (
    (248, 246, 237), (247, 242, 249), (242, 248, 243), (246, 246, 240),
    (237, 245, 251), (251, 245, 240), (242, 249, 249), (247, 245, 242),
    (245, 247, 238), (248, 245, 237),
)


def glyph(digit: int, variant: int, rng: random.Random) -> Image.Image:
    canvas = Image.new("L", (W, W), 0)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(
        FONTS[variant % len(FONTS)], round(rng.uniform(129, 146) * FACTOR)
    )
    bounds = draw.textbbox((0, 0), str(digit), font=font, stroke_width=0)
    glyph_x = (W - (bounds[2] - bounds[0])) / 2 - bounds[0]
    glyph_y = (W - (bounds[3] - bounds[1])) / 2 - bounds[1]
    glyph_x += rng.uniform(-8, 8) * FACTOR
    glyph_y += rng.uniform(-7, 7) * FACTOR
    draw.text(
        (int(glyph_x), int(glyph_y)), str(digit), font=font, fill=255,
        stroke_width=rng.choice([0, 1, 2]) * FACTOR, stroke_fill=255,
    )
    canvas = canvas.rotate(
        rng.uniform(-22, 22), resample=Image.Resampling.BICUBIC, fillcolor=0
    )

    # Deformacao senoidal local: nao equivale apenas a rodar o glifo inteiro.
    distorted = Image.new("L", (W, W), 0)
    for y in range(W):
        shift = round(
            (6 * math.sin(y / W * 2.5 * math.pi + variant)
             + 2.2 * math.sin(y / W * 8 * math.pi + variant * 0.3)) * FACTOR
        )
        if shift > 0:
            distorted.paste(canvas.crop((0, y, W - shift, y + 1)), (shift, y))
        elif shift < 0:
            distorted.paste(canvas.crop((-shift, y, W, y + 1)), (0, y))
        else:
            distorted.paste(canvas.crop((0, y, W, y + 1)), (0, y))
    return distorted


def damage_strokes(mask: Image.Image, rng: random.Random, case: int) -> Image.Image:
    """Apaga secoes do glifo, rompendo sua conectividade geometrica."""
    draw = ImageDraw.Draw(mask)
    for _ in range(2 + case % 2):
        x = rng.randint(37, 132) * FACTOR
        y = rng.randint(43, 134) * FACTOR
        angle = rng.uniform(-1.25, 1.25)
        length = rng.randint(32, 75) * FACTOR
        dx, dy = length * math.cos(angle), length * math.sin(angle)
        draw.line(
            (int(x - dx / 2), int(y - dy / 2),
             int(x + dx / 2), int(y + dy / 2)),
            fill=0, width=rng.randint(3, 6) * FACTOR,
        )
    if case in (1, 3, 5, 7, 9):
        x = rng.randint(49, 117) * FACTOR
        y = rng.randint(53, 122) * FACTOR
        width = rng.randint(8, 19) * FACTOR
        height = rng.randint(9, 15) * FACTOR
        draw.polygon(
            [(x-width, y-height//2), (x+width, y-height),
             (x+width//2, y+height), (x-width//2, y+height//2)],
            fill=0,
        )
    return mask


def render(case: int, digit: int) -> Image.Image:
    rng = random.Random(100714 + case * 97)
    ink = INKS[case]
    paper = PAPERS[case]
    mask = damage_strokes(glyph(digit, case, rng), rng, case)

    base = Image.new("RGB", (W, W), paper)
    pixels = base.load()
    coverage_mask = mask.load()
    for y in range(W):
        for x in range(W):
            rough = rng.randrange(-7, 8)
            lighting = (
                2.3 * math.sin(x / (W / 6))
                + 3.2 * math.cos(y / (W / 7))
            )
            background = tuple(
                round(min(255, max(0, value + rough + lighting)))
                for value in paper
            )
            coverage = coverage_mask[x, y] / 255 * (0.72 + 0.27 * rng.random())
            pixels[x, y] = tuple(
                round(background[i] * (1 - coverage) + ink[i] * coverage)
                for i in range(3)
            )

    draw = ImageDraw.Draw(base, "RGBA")
    # Fragmentos da mesma cor/espessura dos tracos, confundindo a separacao.
    for _ in range(10 + (case % 3) * 3):
        x = rng.randint(22, 164) * FACTOR
        y = rng.randint(26, 168) * FACTOR
        dx = rng.randint(-15, 15) * FACTOR
        dy = rng.randint(-17, 17) * FACTOR
        draw.line(
            [(x, y), (x + dx, y + dy)],
            fill=(*ink, rng.randint(125, 225)),
            width=rng.randint(2, 5) * FACTOR, joint="curve",
        )

    # Tres ou quatro curvas de interferencia cruzam o proprio digito.
    for _ in range(3 + case % 2):
        start_x = rng.randint(2, 20) * FACTOR
        end_x = rng.randint(166, 189) * FACTOR
        y_base = rng.randint(43, 147) * FACTOR
        amplitude = rng.randint(9, 27) * FACTOR
        phase = rng.uniform(-math.pi, math.pi)
        points = []
        for index in range(65):
            x = start_x + (end_x - start_x) * index / 64
            y = (
                y_base + amplitude * math.sin(2 * math.pi * index / 64 + phase)
                + 10 * FACTOR
                * math.sin(4 * math.pi * index / 64 + phase / 2)
            )
            points.append((round(x), round(y)))
        interfering_ink = tuple(
            max(0, min(255, ink[i] + rng.randint(-24, 30)))
            for i in range(3)
        )
        draw.line(
            points, fill=(*interfering_ink, rng.randint(142, 218)),
            width=rng.randint(2, 4) * FACTOR, joint="curve",
        )

    # Pequenos riscos e particulas no entorno, sem mais glifos completos.
    for _ in range(16 + case):
        x = rng.randint(20, 173) * FACTOR
        y = rng.randint(20, 173) * FACTOR
        dx = rng.randint(-8, 8) * FACTOR
        dy = rng.randint(-8, 8) * FACTOR
        draw.line(
            (x, y, x + dx, y + dy),
            fill=(*ink, rng.randint(75, 150)),
            width=rng.randint(1, 2) * FACTOR,
        )
    for _ in range(75):
        x, y = rng.randrange(W), rng.randrange(W)
        radius = rng.randint(1, 3) * FACTOR
        draw.ellipse(
            (x-radius, y-radius, x+radius, y+radius),
            fill=(*ink, rng.randint(15, 80)),
        )
    return base.resize((SIZE, SIZE), Image.Resampling.LANCZOS).filter(
        ImageFilter.GaussianBlur(0.35)
    )


def gerar(output: Path = OUTPUT) -> None:
    assert sorted(DIGITS) == list(range(10))
    output = output.resolve()
    if output == Path(__file__).resolve().parent:
        raise ValueError("A pasta oficial esta reservada; escolha outra pasta")
    if output.exists() and any(output.iterdir()):
        raise ValueError("A pasta de destino deve estar vazia; resultados anteriores sao preservados")
    output.mkdir(parents=True, exist_ok=True)
    for index, digit in enumerate(DIGITS):
        target = output / f"caso_{index+1:02}.png"
        render(index, digit).save(target, format="PNG", optimize=True)
        print("Gerado:", target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT,
                        help="Pasta vazia para um conjunto separado; nunca a pasta oficial")
    args = parser.parse_args()
    gerar(args.output_dir)
