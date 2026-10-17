"""Independent labelled corruptions with clean sources and foreground annotations.

Only supplied MNIST indices and open fonts are used. No course challenge inputs,
labels, generator or previously completed prediction caches are accessed.
"""

from functools import lru_cache
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import torch

from .preprocess import prepare

CONDITIONS = ("clean", "background", "crossing_lines", "blur_jpeg", "short_gaps", "mixed")


@lru_cache(maxsize=32)
def get_font(path):
    return ImageFont.truetype(path, 84)


def glyph_mask(rng, digit, source, font):
    if source is None:
        face = get_font(str(font))
        box = face.getbbox(str(digit))
        glyph = Image.new("L", (box[2] - box[0] + 4, box[3] - box[1] + 4))
        ImageDraw.Draw(glyph).text((2 - box[0], 2 - box[1]), str(digit), fill=255, font=face)
    else:
        glyph = Image.fromarray(source)
    glyph = glyph.crop(glyph.getbbox())
    height = int(rng.integers(49, 77))
    width = max(8, min(80, round(height * glyph.width / glyph.height * rng.uniform(.85, 1.15))))
    glyph = glyph.resize((width, height), Image.Resampling.BICUBIC)
    glyph = glyph.rotate(float(rng.uniform(-12, 12)), Image.Resampling.BICUBIC, expand=True)
    canvas = Image.new("L", (128, 128))
    x = (128 - glyph.width) // 2 + int(rng.integers(-8, 9))
    y = (128 - glyph.height) // 2 + int(rng.integers(-8, 9))
    canvas.paste(glyph, (x, y))
    return canvas


def corrupt(rng, clean, mask, condition, background, foreground):
    image = clean.copy()
    side = image.width
    if condition in ("background", "mixed"):
        yy, xx = np.indices((side, side))
        gradient = ((xx / side - .5) * rng.uniform(-22, 22)
                    + (yy / side - .5) * rng.uniform(-22, 22))
        pixels = np.asarray(image).astype(np.float32) + gradient[:, :, None]
        pixels += rng.normal(0, rng.uniform(.5, 2), pixels.shape)
        image = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
        draw = ImageDraw.Draw(image)
        for _ in range(int(rng.integers(8, 25))):
            x, y = (int(v) for v in rng.integers(3, side - 3, 2))
            blend = rng.uniform(.12, .35)
            color = tuple(round(b * (1 - blend) + f * blend) for b, f in zip(background, foreground))
            draw.ellipse((x, y, x + 1, y + 1), fill=color)
    if condition in ("crossing_lines", "mixed"):
        draw = ImageDraw.Draw(image)
        for _ in range(int(rng.integers(1, 4))):
            blend = rng.uniform(.2, .6)
            color = tuple(round(b * (1 - blend) + f * blend) for b, f in zip(background, foreground))
            level, phase = rng.uniform(15, side - 15), rng.uniform(0, 2 * np.pi)
            slope, amplitude = rng.uniform(-.2, .2), rng.uniform(2, 7)
            points = [(x, round(level + slope * (x - side / 2) + amplitude * np.sin(x / 16 + phase)))
                      for x in range(3, side - 3, 2)]
            draw.line(points, fill=color, width=int(rng.integers(1, 3)))
    if condition in ("short_gaps", "mixed"):
        # Erase small glyph fragments, with an explicit upper bound on lost ink.
        visible = np.asarray(mask) > 64
        yy, xx = np.where(visible)
        candidate = image.copy()
        draw = ImageDraw.Draw(candidate)
        erased = np.zeros(visible.shape, dtype=bool)
        for _ in range(2):
            at = int(rng.integers(len(yy)))
            x, y = int(xx[at]), int(yy[at])
            draw.line((x, y, x + 3, y), fill=background, width=1)
            erased[y, x:min(side, x + 4)] = True
        if (erased & visible).sum() <= .08 * visible.sum():
            image = candidate
    if condition in ("blur_jpeg", "mixed"):
        image = image.filter(ImageFilter.GaussianBlur(float(rng.uniform(.25, .7))))
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=int(rng.integers(60, 92)))
        with Image.open(BytesIO(buffer.getvalue())) as decoded:
            image = decoded.convert("RGB")
    return image.convert("RGBA")


def render_pair(rng, digit, source, font, condition):
    mask = glyph_mask(rng, digit, source, font)
    background = tuple(int(v) for v in rng.integers(220, 256, 3))
    foreground = tuple(int(v) for v in rng.integers(5, 65, 3))
    if rng.random() < .15:
        background, foreground = foreground, background
    clean = Image.new("RGB", mask.size, background)
    clean.paste(foreground, (0, 0, *mask.size), mask)
    return (clean.convert("RGBA"),
            corrupt(rng, clean, mask, condition, background, foreground),
            corrupt(rng, clean, mask, condition, background, foreground), mask)


def trace_crop(image, mask):
    """Measure the existing crop against annotations; never feed annotations to inference."""
    pixels = np.asarray(image).astype(np.float64)
    alpha = pixels[:, :, 3] / 255
    gray = (pixels[:, :, 0] * .299 + pixels[:, :, 1] * .587 + pixels[:, :, 2] * .114) * alpha + 255 * (1 - alpha)
    border = np.concatenate([gray[0], gray[-1], gray[1:-1, 0], gray[1:-1, -1]])
    ink = np.abs(gray - border.mean()) / 255
    ink /= ink.max()
    yy, xx = np.where(ink > .20)
    top, bottom, left, right = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
    truth = np.asarray(mask).astype(np.float64) / 255
    gy, gx = np.where(truth > .20)
    glyph_height, glyph_width = gy.max() - gy.min() + 1, gx.max() - gx.min() + 1
    scale = 48 / max(bottom - top, right - left)
    return {"crop_glyph_mass_retained": float(truth[top:bottom, left:right].sum() / truth.sum()),
            "crop_area_over_glyph_box": float((bottom - top) * (right - left) / (glyph_height * glyph_width)),
            "glyph_long_side_after_resize": float(max(glyph_height, glyph_width) * scale),
            "crop_box": [int(v) for v in (left, top, right, bottom)]}


def make_set(images, labels, indices, fonts, count, seed, fixtures=None, annotations=False):
    """Balance every digit/source/condition cell; use only supplied source indices."""
    if count % 120:
        raise ValueError("Count must be a multiple of 120 for balanced cells")
    rng = np.random.default_rng(seed)
    by_digit = [indices[labels[indices] == digit] for digit in range(10)]
    if not fonts or any(not len(group) for group in by_digit):
        raise ValueError("Require fonts and source examples of all ten digits")
    # The anchor is noisy; another corruption and the clean source form two views.
    views = np.empty((count, 3, 1, 64, 64), np.float32)
    targets = np.empty(count, np.int64)
    conditions, printed_flags, records = [], [], []
    for i in range(count):
        digit = i % 10
        printed = (i // 10) % 2 == 0
        condition = CONDITIONS[(i // 20) % len(CONDITIONS)]
        index = int(rng.choice(by_digit[digit]))
        clean, first, second, mask = render_pair(
            rng, digit, None if printed else images[index], fonts[int(rng.integers(len(fonts)))], condition)
        for j, image in enumerate((first, second, clean)):
            views[i, j] = prepare(np.asarray(image), 64)
        targets[i] = digit
        conditions.append(condition)
        printed_flags.append(printed)
        record = {"index": i, "label": digit, "printed": printed,
                  "source_index": None if printed else index, "condition": condition}
        if annotations:
            record.update(trace_crop(first, mask))
        if fixtures is not None and i < 120:
            fixtures.mkdir(parents=True, exist_ok=True)
            prefix = f"sample-{i:03d}"
            for suffix, image in (("raw", first), ("clean", clean), ("mask", mask)):
                image.save(fixtures / f"{prefix}-{suffix}.png")
            record["raw_file"] = f"{prefix}-raw.png"
        records.append(record)
    return {"views": torch.from_numpy(views), "labels": torch.from_numpy(targets),
            "conditions": np.array(conditions), "printed": np.array(printed_flags), "records": records}
