"""Exercise 2: a map of real sentence embeddings; click a phrase to see its nearest neighbours."""

from __future__ import annotations

import argparse
import textwrap

import matplotlib.image as mpimg
import numpy as np
from matplotlib.backend_bases import MouseEvent
from matplotlib.transforms import Bbox
from matplotlib.widgets import TextBox

from apoio_linguagem import lm_studio
from apoio_linguagem.interface_base import (
    INK, MUTED, ORANGE, STATUS, TEAL, add_buttons, add_footer, create_window, generated_image, run_window,
)
from apoio_linguagem.mapa_embeddings import (
    BANK_ANCHORS, BANK_SENTENCES, LABELS, SUGGESTIONS, EmbeddingSource, FallbackEmbeddingSource,
    LiveEmbeddingSource, Projection, RecordedEmbeddingSource, all_base_texts, area_of, nearest, record_all,
)

AREA_COLORS = {"Manutenção": "#4285b4", "Qualidade": "#548348", "Logística": "#b96c8c", "Finanças": "#8863bc"}
ADDED_COLOR = ORANGE
BANK_IMAGE = "banco_dois_sentidos.png"
# Label positions tried around each point (points offset, alignment), nearest first.
LABEL_OFFSETS = ((7, 5, "left"), (7, -16, "left"), (-7, 5, "right"), (-7, -16, "right"),
                 (7, 17, "left"), (-7, 17, "right"), (7, -28, "left"), (-7, -28, "right"))


def short(text: str, width: int = 26) -> str:
    """Short label for the map: the prepared label of a base phrase, or the phrase shortened."""
    if text in LABELS:
        return LABELS[text]
    return text if len(text) <= width else text[:width - 1] + "…"


class EmbeddingMapInterface:
    """Phrases of four areas in 2D; neighbours are computed in the full vector space."""

    def __init__(self, source: EmbeddingSource) -> None:
        self.source = source
        self.texts = all_base_texts()
        self.vectors = source.vectors(self.texts)
        self.projection = Projection(self.vectors, [area_of(text) for text in self.texts])
        self.points = self.projection.project(self.vectors)
        self.added: list[str] = []
        self.selected: int | None = None
        self.bank_mode = False
        self.suggestion_index = 0
        self.message = "Clica num ponto para ver as frases mais próximas, ou escreve uma frase nova."
        self.figure = create_window("Mapa de embeddings", "Mapa de embeddings: frases parecidas ficam perto",
                                    "Cada ponto é uma frase transformada num vetor pelo modelo de embeddings e "
                                    "desenhada em 2D.")
        self.textbox = TextBox(self.figure.add_axes((0.15, 0.80, 0.80, 0.055)), "Nova frase: ", color="white",
                               hovercolor="#f2f8f9")
        self.textbox.label.set_fontsize(14)
        self.textbox.text_disp.set_fontsize(15)
        self.textbox.on_submit(self.add_phrase)
        self.map_axis = self.figure.add_axes((0.05, 0.17, 0.56, 0.58))
        self.panel = self.figure.text(0.64, 0.74, "", fontsize=13.5, va="top", color=INK, linespacing=1.55)
        # The «banco» illustration of the slides, shown in «banco» mode once the trainer has generated it.
        self.bank_image = generated_image(BANK_IMAGE)
        self.bank_axis = self.figure.add_axes((0.64, 0.15, 0.32, 0.22))
        self.bank_axis.axis("off")
        self.status = self.figure.text(0.05, 0.125, "", fontsize=13, color=STATUS)
        self.buttons = add_buttons(self.figure, [
            ("Sugestão de frase", self.add_suggestion), ("Modo «banco»", self.toggle_bank), ("Limpar", self.clear),
        ], y=0.045, x=0.64, width=0.1, gap=0.01)
        for button in self.buttons:
            button.label.set_fontsize(11)  # three buttons share the width of the side panel
        add_footer(self.figure, f"Embeddings reais ({lm_studio.EMBEDDING_MODEL}, 1024 números por frase) · vista 2D: o "
                                "plano que separa as médias das áreas · semelhanças calculadas nos vetores completos")
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)
        self.render()

    def add_phrase(self, text: str) -> None:
        """Embed a new phrase and place it on the map."""
        text = text.strip()
        if not text or text in self.texts:
            return
        try:
            vector = self.source.vectors([text])
        except lm_studio.LmStudioError as error:
            self.message = f"{str(error).rstrip('.')}. Sem LM Studio, usa «Sugestão de frase»."
            self.render()
            return
        self.texts.append(text)
        self.added.append(text)
        self.vectors = np.vstack([self.vectors, vector])
        self.points = np.vstack([self.points, self.projection.project(vector)])
        self.selected = len(self.texts) - 1
        self.message = f"Acrescentada: «{text}»."
        self.render()

    def add_suggestion(self, event: MouseEvent | None = None) -> None:
        """Add the next prepared phrase (works with the recording)."""
        text = SUGGESTIONS[self.suggestion_index % len(SUGGESTIONS)]
        self.suggestion_index += 1
        self.add_phrase(text)

    def toggle_bank(self, event: MouseEvent | None = None) -> None:
        """Show how the two «banco» sentences relate to a money phrase and a garden phrase."""
        self.bank_mode = not self.bank_mode
        self.message = ("Modo «banco»: a mesma palavra, dois sentidos." if self.bank_mode
                        else "Modo «banco» desligado.")
        self.render()

    def clear(self, event: MouseEvent | None = None) -> None:
        base = len(all_base_texts())
        self.texts, self.added = self.texts[:base], []
        self.vectors, self.points = self.vectors[:base], self.points[:base]
        self.selected, self.bank_mode = None, False
        self.textbox.set_val("")
        self.message = "Mapa reposto."
        self.render()

    def on_click(self, event: MouseEvent) -> None:
        """Select the closest point to the click."""
        if event.inaxes is not self.map_axis or event.xdata is None:
            return
        span = np.ptp(self.points, axis=0) + 1e-9
        distances = np.linalg.norm((self.points - (event.xdata, event.ydata)) / span, axis=1)
        if distances.min() < 0.06:
            self.selected = int(distances.argmin())
            self.message = f"Selecionada: «{self.texts[self.selected]}»."
            self.render()

    def _draw_points(self) -> None:
        axis = self.map_axis
        for index, (text, (x, y)) in enumerate(zip(self.texts, self.points)):
            area = area_of(text)
            color = AREA_COLORS.get(area, ADDED_COLOR)
            marker, size = ("o", 90) if area else ("*", 320)
            axis.scatter(x, y, s=size, color=color, marker=marker, edgecolor="white", linewidth=1, zorder=3)
        for area, color in AREA_COLORS.items():
            axis.scatter([], [], color=color, label=area, s=70)
        legend = axis.legend(loc="lower right", fontsize=11, frameon=False)
        self._draw_labels(legend.get_window_extent(self.figure.canvas.get_renderer()))

    def _label_order(self) -> list[int]:
        """Selected phrase first, then the new phrases, then the base phrases."""
        first = [self.selected] if self.selected is not None else []
        added = [i for i, text in enumerate(self.texts) if not area_of(text) and i not in first]
        return first + added + [i for i in range(len(self.texts)) if i not in first and i not in added]

    def _marker_boxes(self) -> list[Bbox]:
        """Screen boxes of the points, so labels are not written over another point."""
        boxes = []
        for text, point in zip(self.texts, self.points):
            x, y = self.map_axis.transData.transform(point)
            half = 6 if area_of(text) else 10  # circles are smaller than the stars of new phrases
            boxes.append(Bbox.from_extents(x - half, y - half, x + half, y + half))
        return boxes

    def _draw_labels(self, legend_box: Bbox) -> None:
        """Place each label where it stays inside the map without touching another label or the legend."""
        axis = self.map_axis
        renderer = self.figure.canvas.get_renderer()
        frame = axis.get_window_extent(renderer)
        placed = [legend_box] + self._marker_boxes()
        for index in self._label_order():
            text, (x, y) = self.texts[index], self.points[index]
            is_priority = index == self.selected or not area_of(text)
            fallback = None
            for dx, dy, align in LABEL_OFFSETS:
                label = axis.annotate(short(text), (x, y), xytext=(dx, dy), textcoords="offset points", ha=align,
                                      fontsize=12, color=AREA_COLORS.get(area_of(text), ADDED_COLOR),
                                      weight="bold" if index == self.selected else "normal")
                box = label.get_window_extent(renderer)
                inside = frame.x0 <= box.x0 and box.x1 <= frame.x1 and frame.y0 <= box.y0 and box.y1 <= frame.y1
                if inside and not any(box.overlaps(other) for other in placed):
                    placed.append(box)
                    break
                label.remove()
                if inside and fallback is None:
                    fallback = (dx, dy, align)
            else:
                # Crowded spot: base phrases lose their label (the point stays clickable); the selected
                # phrase and new phrases keep theirs at the first position inside the map.
                if is_priority and fallback is not None:
                    dx, dy, align = fallback
                    axis.annotate(short(text), (x, y), xytext=(dx, dy), textcoords="offset points", ha=align,
                                  fontsize=12, color=AREA_COLORS.get(area_of(text), ADDED_COLOR),
                                  weight="bold" if index == self.selected else "normal")

    def _draw_neighbours(self) -> str:
        if self.selected is None:
            return "Clica num ponto do mapa."
        text, vector = self.texts[self.selected], self.vectors[self.selected]
        neighbours = nearest(text, vector, self.texts, self.vectors)
        origin = self.points[self.selected]
        lines = [textwrap.fill(f"«{text}»", 40), "", "Mais próximas (semelhança, 0 a 1):"]
        for neighbour in neighbours:
            target = self.points[self.texts.index(neighbour.text)]
            self.map_axis.plot(*zip(origin, target), color=TEAL, linewidth=1.5 + 4 * max(0.0, neighbour.similarity),
                               alpha=0.55, zorder=2)
            area = area_of(neighbour.text) or "frase nova"
            lines.append(f"  {neighbour.similarity:.2f}  {short(neighbour.text, 28)} · {area}")
        return "\n".join(lines)

    def _bank_panel(self) -> str:
        try:
            sentences = self.source.vectors(list(BANK_SENTENCES))
            anchors = self.source.vectors(list(BANK_ANCHORS))
        except lm_studio.LmStudioError as error:
            return f"Modo «banco» indisponível: {error}"
        similarity = sentences @ anchors.T
        for vector, marker in ((sentences, "*"), (anchors, "D")):
            points = self.projection.project(vector)
            self.map_axis.scatter(points[:, 0], points[:, 1], marker=marker, s=260 if marker == "*" else 110,
                                  color=ORANGE if marker == "*" else MUTED, zorder=4)
        lines = ["Modo «banco»: semelhança de cada frase", "com uma frase de dinheiro e uma de jardim:", ""]
        for sentence, row in zip(BANK_SENTENCES, similarity):
            lines.append(f"«{sentence}»")
            lines.extend(f"  {value:.2f}  {anchor}" for anchor, value in zip(BANK_ANCHORS, row))
        return "\n".join(lines)

    def render(self) -> None:
        """Redraw the map, the neighbour lines and the side panel."""
        self.map_axis.clear()
        self.map_axis.set_xticks(())
        self.map_axis.set_yticks(())
        self.map_axis.set_facecolor("white")
        self._draw_points()
        self.panel.set_text(self._bank_panel() if self.bank_mode else self._draw_neighbours())
        self.bank_axis.clear()
        self.bank_axis.axis("off")
        if self.bank_mode and self.bank_image is not None:
            self.bank_axis.imshow(mpimg.imread(self.bank_image))
        self.status.set_text(self.message)
        self.figure.canvas.draw_idle()


def create_source() -> EmbeddingSource:
    """Live embedding model when available, with the recording as fallback."""
    try:
        recorded = RecordedEmbeddingSource()
    except lm_studio.LmStudioError:
        recorded = None
    live = LiveEmbeddingSource() if lm_studio.is_model_available(lm_studio.EMBEDDING_MODEL) else None
    if live is None and recorded is None:
        raise SystemExit(f"Sem LM Studio ({lm_studio.EMBEDDING_MODEL}) e sem gravação de embeddings.")
    return FallbackEmbeddingSource(live, recorded)


def main() -> None:
    """Open the map, or record the vectors with --gravar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gravar", action="store_true", help="grava os vetores das frases preparadas")
    if parser.parse_args().gravar:
        if not lm_studio.is_model_available(lm_studio.EMBEDDING_MODEL):
            raise SystemExit(f"Para gravar é preciso o LM Studio com o modelo {lm_studio.EMBEDDING_MODEL}.")
        print(f"Gravados {record_all(LiveEmbeddingSource())} vetores.")
        return
    source = RecordedEmbeddingSource() if lm_studio.is_offline_forced() else create_source()
    interface = EmbeddingMapInterface(source)

    def smoke() -> None:
        interface.selected = 0
        interface.render()
        print(interface.panel.get_text().splitlines()[3])

    run_window(interface.figure, smoke)


if __name__ == "__main__":
    main()
