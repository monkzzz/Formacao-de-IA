"""Balanced independent glyph/corruption data; no course challenge access."""

from functools import lru_cache
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CONDITIONS = ("clean", "crossing_lines", "speckles", "short_gaps", "blur_jpeg", "mixed")
SOURCES = ("printed", "mnist", "emnist")


@lru_cache(maxsize=96)
def face(path, variation):
    font = ImageFont.truetype(path, 82)
    try:
        axes = font.get_variation_axes()
        fraction = (.30, .50, .70)[variation]
        font.set_variation_by_axes([a["minimum"] + fraction * (a["maximum"] - a["minimum"]) for a in axes])
    except OSError:
        pass  # Static font faces retain their documented shape.
    return font


def render(rng, digit, source, font_path, condition, severity):
    if condition not in CONDITIONS or severity not in (0, 1, 2):
        raise ValueError("Unknown corruption condition or severity")
    variation = int(rng.integers(3)) if source is None else None
    if source is None:
        font = face(str(font_path), variation)
        box = font.getbbox(str(digit))
        mark = Image.new("L", (box[2] - box[0] + 6, box[3] - box[1] + 6))
        ImageDraw.Draw(mark).text((3 - box[0], 3 - box[1]), str(digit), font=font, fill=255)
    else:
        mark = Image.fromarray(source)
    bounds = mark.getbbox()
    if bounds is None:
        raise ValueError("Blank labelled source")
    mark = mark.crop(bounds)
    height = int(rng.integers(48, 81))
    width = max(9, min(80, round(height * mark.width / mark.height * rng.uniform(.78, 1.24))))
    mark = mark.resize((width, height), Image.Resampling.BICUBIC)
    shear = float(rng.uniform(-.12, .12))
    mark = mark.transform(mark.size, Image.Transform.AFFINE, (1, shear, -shear * mark.height / 2, 0, 1, 0), Image.Resampling.BILINEAR)
    mark = mark.rotate(float(rng.uniform(-14, 14)), Image.Resampling.BICUBIC, expand=True)
    mask = Image.new("L", (128, 128))
    x, y = (128 - mark.width) // 2 + int(rng.integers(-5, 6)), (128 - mark.height) // 2 + int(rng.integers(-5, 6))
    mask.paste(mark, (x, y))
    mass = float(np.asarray(mark).sum())
    retained = float(np.asarray(mask).sum()) / mass if mass else 0.
    if retained < .99:
        raise ValueError("Label geometry was clipped")
    background = tuple(int(v) for v in rng.integers(215, 256, 3))
    foreground = tuple(int(v) for v in rng.integers(5, 65, 3))
    if rng.random() < .20:
        background, foreground = foreground, background
    image = Image.new("RGB", mask.size, background)
    image.paste(foreground, (0, 0, *mask.size), mask)
    erased_fraction = 0.
    if condition in ("short_gaps", "mixed"):
        glyph = np.asarray(mask) > 64
        yy, xx = np.where(glyph)
        erased = np.zeros(glyph.shape, bool)
        draw = ImageDraw.Draw(image)
        for _ in range(1 + severity):
            at = int(rng.integers(len(yy)))
            px, py = int(xx[at]), int(yy[at])
            candidate = erased.copy()
            candidate[py, px:min(128, px + 3 + severity)] = True
            if (candidate & glyph).sum() <= .08 * glyph.sum():
                erased = candidate
                draw.line((px, py, min(127, px + 2 + severity), py), fill=background, width=1)
        erased_fraction = float((erased & glyph).sum() / glyph.sum())
    draw = ImageDraw.Draw(image)
    if condition in ("crossing_lines", "mixed"):
        for _ in range(1 + severity):
            opacity = float(rng.uniform(.20, .40 + .18 * severity))
            color = tuple(round(b * (1 - opacity) + f * opacity) for b,f in zip(background, foreground))
            level, phase = rng.uniform(20, 108), rng.uniform(0, 2 * np.pi)
            slope, amplitude = rng.uniform(-.45, .45), rng.uniform(2, 6 + 2 * severity)
            points = [(px, round(level + slope * (px - 64) + amplitude * np.sin(px / 17 + phase))) for px in range(1, 128, 2)]
            draw.line(points, fill=color, width=1 + int(severity == 2 and rng.random() < .5))
    if condition in ("speckles", "mixed"):
        for _ in range(10 + severity * 10):
            px, py = (int(v) for v in rng.integers(2, 125, 2))
            opacity = float(rng.uniform(.12, .4 + .1 * severity))
            color = tuple(round(b * (1 - opacity) + f * opacity) for b,f in zip(background, foreground))
            radius = int(rng.integers(0, 2))
            draw.ellipse((px, py, px + radius, py + radius), fill=color)
        pixels = np.asarray(image).astype(np.float64)
        yy, xx = np.indices((128, 128))
        gradient = (xx / 128 - .5) * rng.uniform(-14, 14) + (yy / 128 - .5) * rng.uniform(-14, 14)
        pixels += gradient[:, :, None] + rng.normal(0, .5 + severity * .4, pixels.shape)
        image = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    if condition in ("blur_jpeg", "mixed"):
        image = image.filter(ImageFilter.GaussianBlur(float(rng.uniform(.10, .25 + severity * .15))))
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=int(rng.integers(65 - severity * 6, 96)))
        with Image.open(BytesIO(buffer.getvalue())) as decoded:
            image = decoded.convert("RGB")
    return image.convert("RGBA"), {"glyph_mass_retained": retained, "erased_glyph_fraction": erased_fraction,
                                   "font_axis_setting": variation}


def make_set(mnist, mnist_labels, mnist_indices, emnist, emnist_labels, emnist_indices, fonts, count, seed, fixtures=None):
    if count < 540 or count % 540 or not fonts:
        raise ValueError("Require nonempty fonts and a multiple of 540 balanced cells")
    from .preprocess import prepare
    rng = np.random.default_rng(seed)
    pools = [[indices[labels[indices] == digit] for digit in range(10)] for labels,indices in
             ((mnist_labels, mnist_indices), (emnist_labels, emnist_indices))]
    if any(not len(p) for group in pools for p in group):
        raise ValueError("All source classes are required")
    inputs = np.empty((count, 1, 64, 64), np.float32)
    labels = np.empty(count, np.int64)
    records = []
    for i in range(count):
        label, source_id = i % 10, (i // 10) % 3
        condition, severity = CONDITIONS[(i // 30) % 6], (i // 180) % 3
        index = None if source_id == 0 else int(rng.choice(pools[source_id - 1][label]))
        source = None if index is None else (mnist if source_id == 1 else emnist)[index]
        font = fonts[int(rng.integers(len(fonts)))]
        image, quality = render(rng, label, source, font, condition, severity)
        inputs[i], labels[i] = prepare(np.asarray(image), 64), label
        row = {"index": i, "label": label, "source": SOURCES[source_id], "source_index": index,
               "condition": condition, "severity": severity, "font": str(font), **quality}
        if fixtures is not None and i < 540:
            fixtures.mkdir(parents=True, exist_ok=True)
            filename = f"sample-{i:04d}.png"
            image.save(fixtures / filename)
            row["file"] = filename
        records.append(row)
    return inputs, labels, records
