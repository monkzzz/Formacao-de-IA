"""Exercise 3: click a word and see which earlier words it consults (didactic attention)."""

from __future__ import annotations

import numpy as np
from matplotlib.backend_bases import MouseEvent
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path
from numpy.typing import NDArray

from apoio_linguagem.interface_base import (
    BOX_FILL, BOX_LINE, INK, MUTED, ORANGE, STATUS, TEAL, add_buttons, add_footer, create_window, run_window,
)

FloatArray = NDArray[np.float64]
TOKENS = ("A", "peça", "era", "frágil", ",", "por", "isso", "coloquei", "-", "a", "na", "caixa", ".")
QUERY_A = 9
# Weights shown on slide «Attention: cada token consulta o contexto»; they must stay identical.
SLIDE_WEIGHTS_A = (0.04, 0.52, 0.03, 0.14, 0.01, 0.02, 0.03, 0.12, 0.01, 0.08)
# Without the mask «a» may also look ahead; «caixa» gains weight (didactic values).
BIDIRECTIONAL_FUTURE_A = {10: 0.03, 11: 0.10, 12: 0.02}
# Didactic links (query index, key index): score added to the default relevance.
LINKS = {
    (2, 1): 2.2, (3, 1): 2.4, (3, 2): 1.2, (4, 3): 1.0, (6, 5): 1.4, (6, 3): 1.6, (7, 6): 1.2, (7, 1): 1.0,
    (8, 7): 1.5, (10, 7): 1.4, (11, 10): 1.6, (11, 7): 1.3, (12, 7): 1.0, (12, 11): 1.0,
    (1, 3): 1.6, (1, 9): 1.2, (1, 11): 0.8, (5, 6): 1.4,
}
DEFAULT_SCORE, SELF_SCORE, PREVIOUS_SCORE = 0.3, 1.0, 0.9


def attention_weights(query: int, causal: bool) -> FloatArray:
    """Didactic attention weights of one query over all tokens; they sum to 1."""
    if not 0 <= query < len(TOKENS):
        raise ValueError(f"Posição fora da frase: {query}")
    if query == QUERY_A:
        weights = np.zeros(len(TOKENS))
        weights[:QUERY_A + 1] = SLIDE_WEIGHTS_A
        if not causal:
            weights *= 1 - sum(BIDIRECTIONAL_FUTURE_A.values())
            for key, weight in BIDIRECTIONAL_FUTURE_A.items():
                weights[key] = weight
        return weights
    scores = np.full(len(TOKENS), DEFAULT_SCORE)
    scores[query] = SELF_SCORE
    if query > 0:
        scores[query - 1] = PREVIOUS_SCORE
    for (source, key), extra in LINKS.items():
        if source == query:
            scores[key] += extra
    if causal:
        scores[query + 1:] = 0.0
    return scores / scores.sum()


def attention_matrix(causal: bool) -> FloatArray:
    """All rows of the didactic attention: row = word that consults, column = word consulted."""
    return np.vstack([attention_weights(query, causal) for query in range(len(TOKENS))])


def chip_layout() -> tuple[FloatArray, FloatArray]:
    """Horizontal centres and widths of the word chips, in axes fractions."""
    widths = np.array([max(0.035, 0.012 + 0.0105 * len(token)) for token in TOKENS])
    gap = 0.008
    start = (1 - widths.sum() - gap * (len(TOKENS) - 1)) / 2
    lefts = start + np.concatenate(([0.0], np.cumsum(widths[:-1] + gap)))
    return lefts + widths / 2, widths


class AttentionInterface:
    """Sentence with arcs from the selected word to the words it consults, plus the full matrix."""

    def __init__(self) -> None:
        self.query = QUERY_A
        self.causal = True
        self.centres, self.widths = chip_layout()
        self.figure = create_window("Attention", "Attention: cada palavra consulta o contexto",
                                    "Clica numa palavra (ou numa linha da matriz) para ver que palavras ela "
                                    "consulta e com que peso.")
        self.sentence_axis = self.figure.add_axes((0.03, 0.53, 0.94, 0.34))
        self.show_matrix = False
        self.matrix_axis = self.figure.add_axes((0.10, 0.24, 0.25, 0.25))
        self.explanation = self.figure.text(0.05, 0.45, "", fontsize=16, va="top", color=INK, linespacing=1.8)
        self.buttons = add_buttons(self.figure, [
            ("Máscara causal", self.toggle_mask), ("Palavra anterior", self.previous_word),
            ("Palavra seguinte", self.next_word), ("Voltar a «a»", self.reset), ("Ver matriz", self.toggle_matrix),
        ])
        add_footer(self.figure, "Pesos didáticos escolhidos à mão (os de «a» são os do slide), não medidos num "
                                "modelo · um modelo real tem muitas cabeças de attention em cada camada")
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)
        self.render()

    def toggle_mask(self, event: MouseEvent | None = None) -> None:
        """Switch between causal (decoder) and bidirectional (encoder) attention."""
        self.causal = not self.causal
        self.render()

    def toggle_matrix(self, event: MouseEvent | None = None) -> None:
        """Show or hide the full matrix (every word against every word)."""
        self.show_matrix = not self.show_matrix
        self.render()

    def previous_word(self, event: MouseEvent | None = None) -> None:
        self.query = (self.query - 1) % len(TOKENS)
        self.render()

    def next_word(self, event: MouseEvent | None = None) -> None:
        self.query = (self.query + 1) % len(TOKENS)
        self.render()

    def reset(self, event: MouseEvent | None = None) -> None:
        self.query, self.causal = QUERY_A, True
        self.render()

    def on_click(self, event: MouseEvent) -> None:
        """Select the clicked word in the sentence or the clicked row of the matrix."""
        if event.inaxes is self.sentence_axis and event.xdata is not None:
            distances = np.abs(self.centres - event.xdata)
            if distances.min() <= self.widths[distances.argmin()]:
                self.query = int(distances.argmin())
                self.render()
        elif self.show_matrix and event.inaxes is self.matrix_axis and event.ydata is not None:
            self.query = int(np.clip(round(event.ydata), 0, len(TOKENS) - 1))
            self.render()

    def _render_sentence(self, weights: FloatArray) -> None:
        axis = self.sentence_axis
        axis.clear()
        axis.set(xlim=(0, 1), ylim=(0, 1))
        axis.axis("off")
        base = 0.22
        for key, weight in enumerate(weights):
            if key == self.query or weight <= 0:
                continue
            start, end = self.centres[self.query], self.centres[key]
            height = min(0.7, 0.12 + 0.75 * abs(start - end))
            path = Path([(start, base), (start, base + height), (end, base + height), (end, base)],
                        [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
            axis.add_patch(PathPatch(path, facecolor="none", edgecolor=ORANGE, linewidth=0.8 + weight * 24,
                                     alpha=0.45 + 0.55 * min(1.0, weight * 3), capstyle="round"))
            if weight >= 0.08:
                axis.text((start + end) / 2, base + 0.75 * height + 0.03, f"{weight:.0%}", ha="center",
                          fontsize=15, weight="bold", color="#b3641d")
        for index, (token, centre, width) in enumerate(zip(TOKENS, self.centres, self.widths)):
            is_query = index == self.query
            is_blocked = self.causal and index > self.query
            fill = ORANGE if is_query else ("#f4f6f7" if is_blocked else BOX_FILL)
            color = "white" if is_query else ("#a7b4b9" if is_blocked else INK)
            axis.add_patch(FancyBboxPatch((centre - width / 2, 0.02), width, 0.18,
                                          boxstyle="round,pad=0,rounding_size=0.01", facecolor=fill,
                                          edgecolor=ORANGE if is_query else BOX_LINE))
            axis.text(centre, 0.11, token, ha="center", va="center", fontsize=18, color=color,
                      weight="bold" if is_query else "normal")

    def _render_matrix(self, matrix: FloatArray) -> None:
        axis = self.matrix_axis
        axis.clear()
        shown = np.ma.masked_where(matrix <= 0, matrix)
        axis.imshow(np.ones_like(matrix), cmap="Greys", vmin=0, vmax=7, aspect="auto")
        axis.imshow(shown, cmap="Oranges", vmin=0, vmax=0.6, aspect="auto")
        axis.add_patch(Rectangle((-0.5, self.query - 0.5), len(TOKENS), 1, fill=False, edgecolor=TEAL, linewidth=2.5))
        axis.set_xticks(range(len(TOKENS)), TOKENS, rotation=90, fontsize=10)
        axis.set_yticks(range(len(TOKENS)), TOKENS, fontsize=10)
        axis.set_ylabel("quem consulta", fontsize=11, color=MUTED)
        # No x label: below the rotated words it would fall under the buttons; the title names the columns.
        axis.set_title("Colunas: palavra consultada (cinzento = 0)", fontsize=12, color=MUTED)

    def _render_explanation(self, weights: FloatArray) -> None:
        token = TOKENS[self.query]
        top = [index for index in np.argsort(-weights) if weights[index] > 0][:3]
        mix = " + ".join(f"{weights[i]:.0%} «{TOKENS[i]}»" for i in top)
        consulted = int((weights > 0).sum())
        mask = ("Máscara ligada: só o passado (modelo que gera texto)." if self.causal
                else "Máscara desligada: também o futuro (encoder).")
        self.explanation.set_text(
            f"«{token}» consulta {consulted} palavras · os pesos somam {weights.sum():.0%}\n"
            f"Novo vetor de «{token}» = {mix} + …\n{mask}"
        )
        self.explanation.set_color(STATUS)
        # With the matrix hidden the explanation takes the whole width, in a larger font.
        self.explanation.set_position((0.45, 0.45) if self.show_matrix else (0.05, 0.42))
        self.explanation.set_fontsize(14 if self.show_matrix else 17)

    def render(self) -> None:
        """Redraw arcs, chips, the optional matrix and the explanation for the selected word."""
        weights = attention_weights(self.query, self.causal)
        self._render_sentence(weights)
        self.matrix_axis.set_visible(self.show_matrix)
        if self.show_matrix:
            self._render_matrix(attention_matrix(self.causal))
        self._render_explanation(weights)
        self.buttons[0].label.set_text("Máscara: " + ("ligada" if self.causal else "desligada"))
        self.buttons[4].label.set_text("Esconder matriz" if self.show_matrix else "Ver matriz")
        self.figure.canvas.draw_idle()


def main() -> None:
    """Open the exercise directly."""
    interface = AttentionInterface()

    def smoke() -> None:
        print(interface.explanation.get_text().splitlines()[1])
        interface.toggle_mask()
        print(interface.explanation.get_text().splitlines()[1])

    run_window(interface.figure, smoke)


if __name__ == "__main__":
    main()
