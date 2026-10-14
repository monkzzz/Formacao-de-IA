#!/usr/bin/env python3
"""Gera dez imagens desafiadoras de digitos (0-9), sem treinar um modelo.

Os nomes sao neutros, mas o gerador e publico. Para um teste cego, os
participantes devem apenas carregar as imagens, nao consultar o codigo.
Requer Pillow. Uso: python Dia2/Desafio/gerar_desafio_avancado.py
"""
from __future__ import annotations

import math
from pathlib import Path
import random
import re

from PIL import Image, ImageDraw, ImageFilter

SIDE = 160
WORK = SIDE * 4
FACTOR = WORK / 224
OUTPUT = Path(__file__).resolve().parent / "Avancado"

# Caminhos originais de caligrafia, independentes de fonte instalada.
PATHS = {
    0: "M 118 45 C 75 40 65 73 69 113 C 73 157 91 185 121 183 C 152 183 166 151 162 107 C 159 69 146 45 118 45",
    1: "M 80 83 Q 105 68 122 47 Q 125 95 121 182 M 92 184 Q 123 182 151 184",
    2: "M 72 78 C 75 43 133 31 157 59 C 181 87 150 114 118 138 C 91 156 77 171 74 183 Q 119 180 162 183",
    3: "M 77 56 C 108 35 149 43 157 68 C 165 93 132 108 111 112 C 149 104 171 129 159 158 C 147 189 105 193 80 171",
    4: "M 145 183 Q 147 100 145 46 M 144 46 C 121 79 92 112 75 140 C 101 143 137 141 165 139",
    5: "M 158 53 C 123 54 105 57 88 58 Q 83 91 82 112 C 105 98 136 106 153 127 C 168 148 155 171 135 181 Q 106 194 77 169",
    6: "M 148 53 C 113 63 85 92 81 123 C 75 154 89 184 119 182 C 147 183 163 161 154 140 C 147 119 113 115 92 132 C 80 143 83 162 92 174",
    7: "M 73 57 C 105 55 136 56 165 53 C 143 98 116 146 105 184 M 89 111 Q 118 117 146 108",
    8: "M 118 112 C 78 93 81 63 104 50 C 129 38 158 57 155 82 C 153 105 123 112 115 115 C 83 128 70 152 85 172 C 103 194 149 187 159 165 C 169 143 144 123 118 112",
    9: "M 148 107 C 154 78 143 54 123 49 C 95 43 76 63 80 89 C 84 114 110 125 130 113 C 146 103 149 91 147 77 C 158 125 136 165 104 185",
}

# Uma imagem por classe, mas ordem e nomes nao revelam os digitos.
CASES = [
    (6, -18, 0.76, (241, 231, 200), (66, 53, 110), "interference"),
    (0, 19, 0.85, (208, 230, 243), (87, 94, 147), "occlusion"),
    (8, -25, 0.75, (235, 210, 221), (104, 46, 89), "double"),
    (3, 16, 0.91, (217, 239, 213), (54, 88, 47), "stroke"),
    (9, -14, 0.67, (236, 218, 180), (105, 82, 120), "noise"),
    (1, 7, 0.75, (218, 207, 249), (80, 65, 144), "underline"),
    (5, -17, 0.82, (215, 231, 220), (58, 105, 101), "occlusion"),
    (2, 21, 0.71, (240, 215, 186), (145, 77, 84), "interference"),
    (7, -23, 0.79, (214, 226, 249), (63, 85, 140), "double"),
    (4, 17, 0.77, (241, 235, 192), (124, 103, 51), "stroke"),
]


def parse_path(source: str) -> list[list[tuple[float, float]]]:
    tokens = re.findall(r"[MLQC]|-?\d+(?:\.\d+)?", source)
    j = 0
    command = ""
    current = (0.0, 0.0)
    strokes: list[list[tuple[float, float]]] = []
    line: list[tuple[float, float]] = []

    def value() -> float:
        nonlocal j
        number = float(tokens[j])
        j += 1
        return number

    while j < len(tokens):
        if tokens[j] in "MLQC":
            command = tokens[j]
            j += 1
        if command == "M":
            current = (value(), value())
            line = [current]
            strokes.append(line)
            command = "L"
            continue
        start = current
        if command == "L":
            current = (value(), value())
            line.append(current)
            continue
        if command == "Q":
            control = (value(), value())
            current = (value(), value())
            for s in range(1, 91):
                t = s / 90
                u = 1 - t
                line.append((u*u*start[0]+2*u*t*control[0]+t*t*current[0],
                             u*u*start[1]+2*u*t*control[1]+t*t*current[1]))
            continue
        if command == "C":
            a = (value(), value())
            b = (value(), value())
            current = (value(), value())
            for s in range(1, 91):
                t = s / 90
                u = 1 - t
                line.append((u**3*start[0]+3*u*u*t*a[0]+3*u*t*t*b[0]+t**3*current[0],
                             u**3*start[1]+3*u*u*t*a[1]+3*u*t*t*b[1]+t**3*current[1]))
            continue
        raise ValueError("Comando inesperado: " + command)
    return strokes


def paint_background(background: tuple[int, int, int], rng: random.Random) -> Image.Image:
    base = Image.new("RGB", (SIDE, SIDE))
    pixels = base.load()
    for y in range(SIDE):
        for x in range(SIDE):
            grain = rng.gauss(0, 4.6)
            gradient = 10 * (x / SIDE - 0.5) + 8 * math.sin((y + 8) / 32)
            pixels[x, y] = tuple(int(max(0, min(255, c + grain + gradient))) for c in background)
    return base


def create_case(index: int, case: tuple) -> Image.Image:
    digit, angle, scale, bg, ink, extra = case
    rng = random.Random(6802026 + index * 179)
    mask = Image.new("L", (WORK, WORK), 0)
    drawer = ImageDraw.Draw(mask)
    x_shift, y_shift = (rng.uniform(-13, 13) * FACTOR, rng.uniform(-10, 10) * FACTOR)
    a = math.radians(angle)
    for stroke in parse_path(PATHS[digit]):
        points = []
        for t, (x, y) in enumerate(stroke):
            dx, dy = x - 112, y - 112
            xx = 112 * FACTOR + (dx*math.cos(a) - dy*math.sin(a)) * scale * FACTOR
            yy = 112 * FACTOR + (dx*math.sin(a) + dy*math.cos(a)) * scale * FACTOR
            xx += x_shift + (2.1 * math.sin(t * 0.13 + index * 0.5)) * FACTOR
            yy += y_shift + (1.7 * math.cos(t * 0.09 + index * 0.3)) * FACTOR
            points.append((xx, yy))
        width = round(rng.uniform(8, 13) * scale * FACTOR)
        drawer.line(points, fill=255, width=width, joint="curve")
        radius = width / 2
        for x, y in [points[0], points[-1]]:
            drawer.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)

    pen = ImageDraw.Draw(mask)
    if extra in ("interference", "double"):
        x0, y0 = rng.choice([(24, 95), (31, 135), (94, 23)])
        x1, y1 = rng.choice([(128, 140), (118, 27), (143, 91)])
        pen.line([(x0*4, y0*4), (x1*4, y1*4)],
                 fill=115 if extra == "interference" else 90, width=rng.randrange(5, 11))
    if extra == "underline":
        pen.line([(51*4, 136*4), (118*4, 145*4)], fill=160, width=17)
    if extra == "stroke":
        pen.line([(27*4, 88*4), (45*4, 100*4), (34*4, 115*4)], fill=115, width=17)
    if extra == "noise":
        for _ in range(10):
            x, y = rng.randrange(16, 145), rng.randrange(12, 148)
            radius = rng.randrange(2, 5) * 4
            pen.ellipse((x*4-radius, y*4-radius, x*4+radius, y*4+radius),
                        fill=rng.randrange(55, 135))
    if extra == "occlusion":
        occlusion = ImageDraw.Draw(mask)
        y0 = rng.choice([65, 83]) * 4
        occlusion.polygon(
            [(5*4, y0), (156*4, y0+30), (156*4, y0+54), (5*4, y0+22)],
            fill=25,
        )

    mask = mask.filter(ImageFilter.GaussianBlur(1.4)).resize(
        (SIDE, SIDE), Image.Resampling.LANCZOS
    )
    base = paint_background(bg, rng)
    pixels = base.load()
    strengths = mask.load()
    for y in range(SIDE):
        for x in range(SIDE):
            alpha = strengths[x, y] / 255 * rng.uniform(0.88, 1)
            if alpha < 0.0001:
                continue
            pixels[x, y] = tuple(
                int(round(pixels[x, y][ch] * (1 - alpha) + ink[ch] * alpha))
                for ch in range(3)
            )
    return base.filter(ImageFilter.GaussianBlur(0.48))


def gerar() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for index, case in enumerate(CASES, start=1):
        target = OUTPUT / f"caso_{index:02d}.png"
        create_case(index, case).save(target, format="PNG", optimize=True)
        print(f"Gerado: {target}")


if __name__ == "__main__":
    gerar()
