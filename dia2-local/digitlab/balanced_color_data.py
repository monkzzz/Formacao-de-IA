"""Balanced geometry-matched legacy and chromatic glyph data, without challenge access."""

import numpy as np
from PIL import Image

from .color_preprocess import prepare_color
from .preprocess import prepare
from .preprocessing_variants import foreground
from .residual import render

KINDS = ("legacy", "color", "isoluminant")


def palette(rng, isoluminant):
    """Sample well-separated colors; optionally constrain grayscale brightness."""
    for _ in range(10000):
        background, ink = rng.integers(15, 241, (2, 3)).astype(float)
        if isoluminant:
            ink[2] = round((background @ np.array([.299, .587, .114]) - .299 * ink[0] - .587 * ink[1]) / .114)
            if not 15 <= ink[2] <= 240:
                continue
        elif abs((background - ink) @ np.array([.299, .587, .114])) < 60:
            continue
        if np.sqrt(np.mean((background - ink) ** 2)) >= 80:
            return background.astype(int), ink.astype(int)
    raise ValueError("Unable to sample color contrast")


def make_raw(images, labels, indices, fonts, count, seed, fixtures=None, kinds=KINDS):
    if count % (20 * len(kinds)) or not fonts or not kinds:
        raise ValueError("Require complete ten-class, two-source, three-kind cells")
    rng = np.random.default_rng(seed)
    pools = [indices[labels[indices] == digit] for digit in range(10)]
    x = np.empty((count, 1, 64, 64), np.float32)
    y = np.empty(count, np.int64)
    gray = np.empty_like(x)
    rejected = np.zeros(count, bool)
    records = []
    for i in range(count):
        digit, printed, kind = i % 10, (i // 10) % 2 == 0, kinds[(i // 20) % len(kinds)]
        source = int(rng.choice(pools[digit]))
        font = fonts[int(rng.integers(len(fonts)))]
        image = render(rng, digit, None if printed else images[source], font)
        colors = None
        if kind != "legacy":
            background, ink = palette(rng, kind == "isoluminant")
            mask = foreground(np.asarray(image))[:, :, None]
            pixels = np.floor(background * (1 - mask) + ink * mask + .5).clip(0, 255).astype(np.uint8)
            image = Image.fromarray(pixels).convert("RGBA")
            colors = [background.tolist(), ink.tolist()]
        rgba = np.asarray(image)
        x[i], y[i] = prepare_color(rgba), digit
        try:
            gray[i] = prepare(rgba, 64)
        except ValueError:
            gray[i] = 0
            rejected[i] = True
        record = {"label": digit, "kind": kind, "printed": printed,
                  "source_index": None if printed else source, "font": font.name,
                  "colors": colors, "grayscale_rejected": bool(rejected[i])}
        if fixtures is not None and i < 180:
            fixtures.mkdir(parents=True, exist_ok=True)
            name = f"sample-{i:04d}.png"
            image.save(fixtures / name)
            record["file"] = name
        records.append(record)
    return {"rgb": x, "gray": gray, "y": y, "gray_rejected": rejected}, records
