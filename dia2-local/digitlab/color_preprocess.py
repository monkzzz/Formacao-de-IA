"""Experimental RGB foreground contract; active grayscale preprocessing is preserved."""

import numpy as np

from .preprocessing_variants import fit_foreground

VERSION = "border-rgb-rms-bilinear-com-64-v1"


def foreground(rgba):
    """Composite on white and measure RGB RMS distance from the mean border."""
    if rgba.ndim != 3 or rgba.shape[2] != 4 or min(rgba.shape[:2]) < 2:
        raise ValueError("Expected an RGBA image at least 2 by 2 pixels")
    if not np.isfinite(rgba).all() or np.any(rgba < 0) or np.any(rgba > 255):
        raise ValueError("Expected finite byte-range RGBA channels")
    pixels = rgba.astype(np.float64)
    alpha = pixels[:, :, 3:4] / 255
    rgb = pixels[:, :, :3] * alpha + 255 * (1 - alpha)
    border = np.concatenate([rgb[0], rgb[-1], rgb[1:-1, 0], rgb[1:-1, -1]])
    distance = np.sqrt(np.mean((rgb - border.mean(axis=0)) ** 2, axis=2)) / 255
    contrast = float(distance.max())
    if contrast < .12:
        raise ValueError("No visible digit: image is blank or has insufficient contrast")
    distance /= contrast
    distance[distance < .06] = 0
    return distance


def prepare_color(rgba, side=64):
    if side not in (28, 64):
        raise ValueError("Supported model input sides are 28 and 64")
    return fit_foreground(foreground(rgba), side)
