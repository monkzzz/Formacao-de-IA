"""Bounded experimental preparation variants; production contracts stay unchanged."""

import math

import numpy as np
from PIL import Image, ImageFilter

from .preprocess import prepare

VARIANTS = ("current", "median_border", "small_components", "median_filter")


def foreground(rgba, median=False):
    pixels = rgba.astype(np.float64)
    alpha = pixels[:, :, 3] / 255
    gray = (pixels[:, :, 0] * .299 + pixels[:, :, 1] * .587 + pixels[:, :, 2] * .114) * alpha + 255 * (1 - alpha)
    border = np.concatenate([gray[0], gray[-1], gray[1:-1, 0], gray[1:-1, -1]])
    background = float(np.median(border) if median else border.mean())
    ink = np.abs(gray - background) / 255
    contrast = float(ink.max())
    if contrast < .12:
        raise ValueError("No visible digit")
    ink /= contrast
    ink[ink < .06] = 0
    return ink


def remove_small(ink):
    mask = ink > 0
    seen = np.zeros(mask.shape, dtype=bool)
    components = []
    height, width = mask.shape
    for y, x in zip(*np.where(mask)):
        if seen[y, x]:
            continue
        stack, component = [(int(y), int(x))], []
        seen[y, x] = True
        while stack:
            yy, xx = stack.pop()
            component.append((yy, xx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = yy + dy, xx + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        components.append(component)
    if not components:
        return ink.copy()
    largest = max(map(len, components))
    maximum = max(4, math.ceil(.0008 * ink.size))
    result = ink.copy()
    for component in components:
        if len(component) < .015 * largest and len(component) < maximum:
            yy, xx = zip(*component)
            result[yy, xx] = 0
    return result


def fit_foreground(ink, side=64):
    """Mirror production crop, pixel-center interpolation and center of mass."""
    rows, cols = np.where(ink > .20)
    if not len(rows):
        raise ValueError("No visible digit")
    crop = ink[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    height, width = crop.shape
    scale = (48 if side == 64 else 20) / max(height, width)
    out_h, out_w = max(1, math.floor(height * scale + .5)), max(1, math.floor(width * scale + .5))
    yy = np.clip((np.arange(out_h) + .5) * height / out_h - .5, 0, height - 1)
    xx = np.clip((np.arange(out_w) + .5) * width / out_w - .5, 0, width - 1)
    y0, x0 = yy.astype(int), xx.astype(int)
    y1, x1 = np.minimum(y0 + 1, height - 1), np.minimum(x0 + 1, width - 1)
    fy, fx = (yy - y0)[:, None], (xx - x0)[None, :]
    resized = ((1 - fy) * ((1 - fx) * crop[y0[:, None], x0] + fx * crop[y0[:, None], x1])
               + fy * ((1 - fx) * crop[y1[:, None], x0] + fx * crop[y1[:, None], x1]))
    mass = resized.sum()
    if mass < 1:
        raise ValueError("Too little foreground")
    cy = float((resized.sum(axis=1) * np.arange(out_h)).sum() / mass)
    cx = float((resized.sum(axis=0) * np.arange(out_w)).sum() / mass)
    center = (side - 1) / 2
    oy, ox = math.floor(center - cy + .5), math.floor(center - cx + .5)
    top, left = max(0, oy), max(0, ox)
    bottom, right = min(side, oy + out_h), min(side, ox + out_w)
    result = np.zeros((side, side), dtype=np.float32)
    result[top:bottom, left:right] = resized[top - oy:bottom - oy, left - ox:right - ox]
    return result[None]


def prepare_variant(rgba, variant, side=64):
    if variant not in VARIANTS or side not in (28, 64):
        raise ValueError("Unknown study variant or input size")
    if rgba.ndim != 3 or rgba.shape[2] != 4 or min(rgba.shape[:2]) < 2:
        raise ValueError("Expected RGBA input")
    if variant == "current":
        return prepare(rgba, side)
    if variant == "median_filter":
        # Composite alpha before filtering, as required by the upload contract.
        source = Image.new("RGBA", (rgba.shape[1], rgba.shape[0]), "white")
        source.alpha_composite(Image.fromarray(rgba))
        image = source.convert("RGB").filter(ImageFilter.MedianFilter(3)).convert("RGBA")
        return prepare(np.asarray(image), side)
    ink = foreground(rgba, median=variant == "median_border")
    if variant == "small_components":
        ink = remove_small(ink)
    return fit_foreground(ink, side)
