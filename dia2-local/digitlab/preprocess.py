"""Contracts mirrored in dist/v3/preprocess.js; the legacy default is preserved."""

import math

import numpy as np

VERSION = "border-gray-bilinear-com-v1"
VERSION64 = "border-gray-bilinear-com-64-v1"


def prepare(rgba: np.ndarray, side=28) -> np.ndarray:
    """Composite on white, estimate border background, crop and center ink.

    Output is float32 CHW (1, side, side), foreground in [0, 1]. Uniform or
    negligible-contrast inputs raise ValueError rather than inventing a digit.
    """
    if side not in (28, 64):
        raise ValueError("Supported model input sides are 28 and 64")
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
    scale = (48 if side == 64 else 20) / max(height, width)
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
    center = (side - 1) / 2
    oy, ox = math.floor(center - cy + .5), math.floor(center - cx + .5)
    result = np.zeros((side, side), dtype=np.float32)
    top, left = max(0, oy), max(0, ox)
    bottom, right = min(side, oy + out_h), min(side, ox + out_w)
    result[top:bottom, left:right] = resized[top - oy:bottom - oy, left - ox:right - ox]
    return result[None]


def prepare_mnist(images: np.ndarray, side=28) -> np.ndarray:
    """Use the same image preparation for training and browser images."""
    result = np.empty((len(images), 1, side, side), dtype=np.float32)
    for index, image in enumerate(images):
        rgba = np.empty((28, 28, 4), dtype=np.uint8)
        rgba[:, :, :3] = image[:, :, None]
        rgba[:, :, 3] = 255
        result[index] = prepare(rgba, side)
    return result
