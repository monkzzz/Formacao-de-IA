"""Shared window layout for the module 2 exercises (title, buttons, footer, headless runs)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from matplotlib.widgets import Button

from .ajuste_janela import fit_window

INK = "#172b33"
TEAL = "#008694"
BLUE = "#00a8cc"
ORANGE = "#d9822b"
ORANGE_FILL = "#fdf1e4"
BOX_FILL = "#e1eff2"
BOX_LINE = "#9fb6bd"
MUTED = "#8a9ba1"
RED = "#c0392b"
BACKGROUND = "#f6fafb"
STATUS = "#005b65"

ButtonAction = tuple[str, Callable[[MouseEvent | None], None]]
# Trainer illustrations bundled with the exercises; provenance is recorded in recursos/README.md.
GENERATED_IMAGES = Path(__file__).resolve().parents[2] / "recursos" / "modulo2"


def generated_image(file_name: str) -> Path | None:
    """Path of a trainer-generated illustration, or None while it does not exist yet."""
    path = GENERATED_IMAGES / file_name
    return path if path.is_file() else None


def is_headless() -> bool:
    """True when the exercises run without windows (tests and smoke runs)."""
    return os.environ.get("FORMACAO_ML_NO_PAUSE") == "1"


def create_window(window_title: str, title: str, subtitle: str, size: tuple[float, float] = (15, 8.6)) -> plt.Figure:
    """Figure with the common title block used by every exercise."""
    figure = plt.figure(figsize=size, facecolor=BACKGROUND)
    fit_window(figure)
    figure.canvas.manager.set_window_title(f"Formação IA · {window_title}")
    figure.suptitle(title, fontsize=23, weight="bold", y=0.97)
    figure.text(0.05, 0.905, subtitle, fontsize=14)
    return figure


def add_buttons(figure: plt.Figure, actions: list[ButtonAction], y: float = 0.09, x: float = 0.05,
                width: float = 0.16, gap: float = 0.02) -> list[Button]:
    """A row of buttons; keep the returned list alive so the callbacks keep working."""
    buttons = []
    for index, (label, callback) in enumerate(actions):
        button = Button(figure.add_axes((x + index * (width + gap), y, width, 0.06)), label,
                        color=BOX_FILL, hovercolor="#c1e3e9")
        button.label.set_fontsize(12)
        button.on_clicked(callback)
        buttons.append(button)
    return buttons


def add_footer(figure: plt.Figure, text: str) -> None:
    """Small grey line with the caveats of the exercise."""
    figure.text(0.05, 0.025, text, fontsize=11, color="#52666d")


def run_window(figure: plt.Figure, smoke: Callable[[], None]) -> None:
    """Show the window, or run a short scripted interaction when headless."""
    try:
        if is_headless():
            smoke()
        else:
            plt.show()
    finally:
        plt.close(figure)
