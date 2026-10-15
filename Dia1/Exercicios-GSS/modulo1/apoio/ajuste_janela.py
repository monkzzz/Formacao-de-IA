"""Keep exercise windows readable on any screen: fit the window and scale every text with it.

The layouts use figure fractions, so they shrink with the window, but font sizes are in points.
On a smaller screen (for example a projector at 1920x1080 with 125% scaling) the window is
reduced to fit and every text is scaled by the same factor, which keeps the drawn layout intact.

The same file exists in the support package of each module (apoio, apoio_linguagem, apoio_agentes)
because each module runs from its own folder; tests/test_ajuste_janela.py keeps the copies identical.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.text import Text

SCREEN_SHARE = (0.96, 0.86)  # leave room for the taskbar, the title bar and the toolbar
SCALE_LIMITS = (0.5, 1.4)
TK_BASE_DPI = 96.0


def fit_window(figure: plt.Figure) -> None:
    """Shrink the window to the screen when needed and keep every text proportional to its size."""
    base_size = figure.get_size_inches().copy()
    _fit_to_screen(figure)

    def rescale(_event: object = None) -> None:
        width, height = figure.get_size_inches()
        low, high = SCALE_LIMITS
        scale = min(max(min(width / base_size[0], height / base_size[1]), low), high)
        changed = False
        for text in figure.findobj(Text):
            applied = getattr(text, "_ajuste_aplicado", None)
            # A size set by the exercise after the last adjustment becomes the new nominal size.
            if applied is None or abs(text.get_fontsize() - applied) > 0.01:
                text._ajuste_base = text.get_fontsize()
            target = text._ajuste_base * scale
            if abs(text.get_fontsize() - target) > 0.01:
                text.set_fontsize(target)
                changed = True
            text._ajuste_aplicado = text.get_fontsize()
        if changed:
            figure.canvas.draw_idle()

    figure.canvas.mpl_connect("draw_event", rescale)


def _fit_to_screen(figure: plt.Figure) -> None:
    try:
        window = figure.canvas.manager.window
        screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
        # TkAgg multiplies the figure dpi by the screen scaling once the window is shown.
        pixel_ratio = window.winfo_fpixels("1i") / TK_BASE_DPI
    except AttributeError:
        return  # no Tk window: tests, headless runs and saved images keep the nominal size
    width, height = figure.get_size_inches()
    needed_width = width * figure.dpi * pixel_ratio
    needed_height = height * figure.dpi * pixel_ratio
    shrink = min(1.0, screen_width * SCREEN_SHARE[0] / needed_width, screen_height * SCREEN_SHARE[1] / needed_height)
    if shrink < 1.0:
        figure.set_size_inches(width * shrink, height * shrink, forward=True)
