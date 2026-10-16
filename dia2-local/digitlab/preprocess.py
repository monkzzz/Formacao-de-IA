"""Versioned preprocessing contract, mirrored exactly in dist/preprocess.js."""

import math

import numpy as np

VERSION = "border-gray-bilinear-com-v1"


def prepare(rgba: np.ndarray) -> np.ndarray:
    """Composite on white, estimate border background, crop and center ink.

    Output is float32 CHW (1, 28, 28), foreground in [0, 1]. Uniform or
    negligible-contrast inputs raise ValueError rather than inventing a digit.
    """
    if rgba.ndim != 3 or rgba.shape[2] != 4 or min(rgba.shape[:2]) < 2:
        raise ValueError("Expected an RGBA image at least 2 by 2 pixels")
    pixels = rgba.astype(np.float64)
    alpha = pixels[:, :, 3] / 255
    gray = (pixels[:, :, 0] * .299 + pixels[:, :, 1] * .587
            + pixels[:, :, 2] * .114) * alpha + 255 * (1 - alpha)
    border = np.concatenate([gray[0], gray[-1], gray[1:-1, 0], gray[1:-1, -1]])
    ink = np.abs(gray - float(border.mean())) / 255
    contrast = float(ink.max())
    if contrast < .12:
        raise ValueError("No visible digit: image is blank or has insufficient contrast")
    ink /= contrast
    ink[ink < .06] = 0
    rows, cols = np.where(ink > .20)
    if not len(rows):
        raise ValueError("No visible digit")
    top, bottom, left, right = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
    crop = ink[top:bottom, left:right]
    height, width = crop.shape
    scale = 20 / max(height, width)
    out_h = max(1, math.floor(height * scale + .5))
    out_w = max(1, math.floor(width * scale + .5))
    # Pixel-center bilinear interpolation with edge clamping, shared with JS.
    yy = np.clip((np.arange(out_h) + .5) * height / out_h - .5, 0, height - 1)
    xx = np.clip((np.arange(out_w) + .5) * width / out_w - .5, 0, width - 1)
    y0, x0 = yy.astype(int), xx.astype(int)
    y1, x1 = np.minimum(y0 + 1, height - 1), np.minimum(x0 + 1, width - 1)
    fy, fx = (yy - y0)[:, None], (xx - x0)[None, :]
    resized = ((1 - fy) * ((1 - fx) * crop[y0[:, None], x0]
                           + fx * crop[y0[:, None], x1])
               + fy * ((1 - fx) * crop[y1[:, None], x0]
                       + fx * crop[y1[:, None], x1]))
    mass = resized.sum()
    if mass < 1:
        raise ValueError("Too little foreground to classify")
    cy = float((resized.sum(axis=1) * np.arange(out_h)).sum() / mass)
    cx = float((resized.sum(axis=0) * np.arange(out_w)).sum() / mass)
    oy, ox = math.floor(13.5 - cy + .5), math.floor(13.5 - cx + .5)
    result = np.zeros((28, 28), dtype=np.float32)
    for y in range(out_h):
        for x in range(out_w):
            if 0 <= oy + y < 28 and 0 <= ox + x < 28:
                result[oy + y, ox + x] = resized[y, x]
    return result[None]


def prepare_mnist(images: np.ndarray) -> np.ndarray:
    """Use the same image preparation for training and browser images."""
    result = np.empty((len(images), 1, 28, 28), dtype=np.float32)
    for index, image in enumerate(images):
        rgba = np.empty((28, 28, 4), dtype=np.uint8)
        rgba[:, :, :3] = image[:, :, None]
        rgba[:, :, 3] = 255
        result[index] = prepare(rgba)
    return result
