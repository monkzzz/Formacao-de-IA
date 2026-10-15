"""Exercise 4: predict the next token with a real local model, choose it and repeat."""

from __future__ import annotations

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent
from matplotlib.patches import Patch
from matplotlib.widgets import Button, Slider

from apoio_linguagem import lm_studio
from apoio_linguagem.ajuste_janela import fit_window
from apoio_linguagem.proximo_token import (
    TOP_CANDIDATES,
    FallbackNextTokenSource,
    LiveNextTokenSource,
    NextTokenSource,
    NextTokenStep,
    NextTokenUnavailable,
    RecordedNextTokenSource,
    choose_most_likely,
    record_contexts,
    sample_candidate,
    save_recording,
    selection_distribution,
)

SEED = 7
MAX_NEW_TOKENS = 12
CONTEXTS = (
    "A produção foi retomada após",
    "A linha 2 parou devido a uma falha no",
    "O sensor da linha 2",
)
MODEL_COLOR = "#cfe3e8"
CHOICE_COLOR = "#00a8cc"
GENERATED_COLOR = "#d9822b"
INK = "#172b33"
MUTED = "#8a9ba1"


def show_token(text: str) -> str:
    """Make spaces visible: a leading space is part of the token."""
    return text.replace(" ", "␣")


def tail_of(text: str, limit: int = 36) -> str:
    """Shorten long contexts from the left, cutting at a word boundary."""
    if len(text) <= limit:
        return text
    cut = text.find(" ", len(text) - limit)
    return "…" + text[cut if cut != -1 else len(text) - limit:]


def decimal(value: float, digits: int) -> str:
    """Number with a Portuguese decimal comma."""
    return f"{value:.{digits}f}".replace(".", ",")


class NextTokenInterface:
    """Grow a sentence token by token from the model's candidate probabilities."""

    def __init__(self, source: NextTokenSource) -> None:
        self.source = source
        self.context_index = 0
        self.generated: list[str] = []
        self.step: NextTokenStep | None = None
        self.random = np.random.default_rng(SEED)
        self.message = ""
        self.figure = plt.figure(figsize=(15, 8.6), facecolor="#f6fafb")
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Próximo token")
        self.figure.suptitle("Prever o próximo token · escolher · repetir", fontsize=23, weight="bold", y=0.97)
        self.figure.text(0.05, 0.905, "O modelo devolve uma probabilidade para cada token possível. "
                         "Escolhemos um, acrescentamo-lo ao texto e pedimos de novo.", fontsize=14)
        self.sentence_axis = self.figure.add_axes((0.05, 0.75, 0.90, 0.12))
        self.bar_axis = self.figure.add_axes((0.24, 0.28, 0.42, 0.40))
        self.panel = self.figure.text(0.71, 0.68, "", fontsize=13, va="top", color=INK, linespacing=1.6)
        self.status = self.figure.text(0.05, 0.185, "", fontsize=14, color="#005b65")
        self.figure.text(0.05, 0.025, f"Probabilidades do modelo {lm_studio.TEXT_MODEL} (LM Studio) para os "
                         f"{TOP_CANDIDATES} tokens mais prováveis · a escolha é feita neste exercício · "
                         "probabilidade alta não significa informação correta", fontsize=11, color="#52666d")
        self._create_controls()
        self.restart()

    def _create_controls(self) -> None:
        self.temperature = Slider(self.figure.add_axes((0.79, 0.31, 0.14, 0.03)), "Temperatura",
                                  0.1, 2.0, valinit=1.0, valstep=0.1, color=CHOICE_COLOR)
        self.top_p = Slider(self.figure.add_axes((0.79, 0.25, 0.14, 0.03)), "Top-p",
                            0.1, 1.0, valinit=1.0, valstep=0.05, color=CHOICE_COLOR)
        for slider, digits in ((self.temperature, 1), (self.top_p, 2)):
            slider.label.set_fontsize(12)
            slider.on_changed(lambda _: self.render())
            # Portuguese decimal comma on the value shown next to the slider.
            slider._format = lambda value, digits=digits: decimal(value, digits)  # noqa: SLF001
            slider.valtext.set_text(decimal(slider.val, digits))
        actions = (
            ("Mais provável", self.choose_greedy), ("Amostrar", self.choose_sample),
            ("Desfazer", self.undo), ("Recomeçar", self.restart), ("Outro contexto", self.next_context),
        )
        self.buttons: list[Button] = []
        for index, (label, callback) in enumerate(actions):
            button = Button(self.figure.add_axes((0.05 + index * 0.18, 0.09, 0.16, 0.06)), label,
                            color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(12)
            button.on_clicked(callback)
            self.buttons.append(button)

    @property
    def context(self) -> str:
        """Starting sentence followed by every chosen token."""
        return CONTEXTS[self.context_index] + "".join(self.generated)

    def _load_step(self) -> None:
        try:
            self.step = self.source.fetch(self.context)
        except (NextTokenUnavailable, lm_studio.LmStudioError) as error:
            self.step = None
            self.message = f"{error} Usa «Recomeçar» ou liga o LM Studio."

    def restart(self, event: MouseEvent | None = None) -> None:
        """Return to the starting sentence and to the initial random seed."""
        self.generated = []
        self.random = np.random.default_rng(SEED)
        self.message = "Começa com «Mais provável» (escolha gulosa) ou «Amostrar» (sorteio pelas probabilidades)."
        self._load_step()
        self.render()

    def next_context(self, event: MouseEvent | None = None) -> None:
        """Cycle through the prepared starting sentences."""
        self.context_index = (self.context_index + 1) % len(CONTEXTS)
        self.restart()

    def undo(self, event: MouseEvent | None = None) -> None:
        """Remove the last chosen token and show its candidates again."""
        if self.generated:
            removed = self.generated.pop()
            self.message = f"Retirado «{show_token(removed)}». Estes eram os candidatos nesse ponto."
            self._load_step()
        self.render()

    def choose_greedy(self, event: MouseEvent | None = None) -> None:
        """Append the candidate with the highest model probability."""
        if self._can_choose():
            self._append(choose_most_likely(self.step), "o mais provável")

    def choose_sample(self, event: MouseEvent | None = None) -> None:
        """Append a candidate drawn with the current temperature and top-p."""
        if self._can_choose():
            index = sample_candidate(self.step, self.temperature.val, self.top_p.val, self.random)
            self._append(index, "sorteado")

    def _can_choose(self) -> bool:
        if self.step is None:
            self.render()
            return False
        if self.step.is_end:
            self.message = "O modelo devolveu o token de fim: a geração termina aqui. «Recomeçar» para repetir."
        elif len(self.generated) >= MAX_NEW_TOKENS:
            self.message = f"Parou no limite de {MAX_NEW_TOKENS} tokens novos (max_tokens), mesmo sem terminar a frase."
        else:
            return True
        self.render()
        return False

    def _append(self, index: int, how: str) -> None:
        option, previous = self.step.options[index], self.step
        self.generated.append(option.text)
        self._load_step()
        if self.step is None:
            # Without the next step the sentence would be stuck; keep the screen as it was.
            self.generated.pop()
            self.step = previous
            self.message = (f"Saiu «{show_token(option.text)}» ({option.probability:.0%}), mas não há resposta "
                            "gravada a partir daí. Volta a amostrar ou liga o LM Studio.")
        else:
            self.message = (f"Escolhido «{show_token(option.text)}» ({how}: {option.probability:.0%}, "
                            f"{index + 1}.º candidato). Agora faz parte do contexto da próxima previsão.")
        self.render()

    def _render_sentence(self) -> None:
        axis = self.sentence_axis
        axis.clear()
        axis.axis("off")
        base, generated = CONTEXTS[self.context_index], "".join(self.generated)
        size = 26 if len(base + generated) < 64 else 20
        first = axis.text(0, 0.62, base, fontsize=size, color=INK, va="center")
        renderer = self.figure.canvas.get_renderer()
        width = first.get_window_extent(renderer).transformed(axis.transAxes.inverted()).width
        axis.text(width, 0.62, generated + " ▌", fontsize=size, color=GENERATED_COLOR, weight="bold", va="center")
        chips = "  ".join(f"[{show_token(token)}]" for token in self.generated) or "(ainda nenhum)"
        axis.text(0, 0.05, f"Tokens escolhidos ({len(self.generated)}/{MAX_NEW_TOKENS}): {chips}",
                  fontsize=13, color=MUTED, va="center")

    def _render_bars(self) -> None:
        axis = self.bar_axis
        axis.clear()
        step = self.step
        if step is None or step.is_end:
            axis.axis("off")
            text = "Sem candidatos para mostrar." if step is None else "Token de fim: o modelo terminou o texto."
            axis.text(0.5, 0.5, text, ha="center", va="center", fontsize=16, color=INK, transform=axis.transAxes)
            return
        axis.axis("on")
        chosen, kept = selection_distribution(step, self.temperature.val, self.top_p.val)
        labels = [show_token(option.text) for option in step.options] + ["outros (resto do vocabulário)"]
        model = [option.probability for option in step.options] + [step.other_probability]
        rows = np.arange(len(labels))
        axis.barh(rows, model, height=0.8, color=MODEL_COLOR, edgecolor="#9fb6bd")
        axis.barh(rows[:-1], chosen, height=0.42, color=CHOICE_COLOR)
        for row, (probability, selected, is_kept) in enumerate(zip(model, chosen, kept)):
            note = f"{probability:.0%}" + (f" → {selected:.0%}" if is_kept else "  excluído")
            axis.text(max(probability, selected) + 0.01, row, note, va="center", fontsize=11,
                      color=INK if is_kept else MUTED)
        axis.text(model[-1] + 0.01, rows[-1], f"{model[-1]:.0%}", va="center", fontsize=11, color=MUTED)
        axis.set_yticks(rows, labels, fontsize=14)
        for label, is_kept in zip(axis.get_yticklabels(), [*kept, False]):
            label.set_color(INK if is_kept else MUTED)
        axis.invert_yaxis()
        axis.set_xlim(0, 1.12)
        axis.set_xticks(())
        axis.spines[["top", "right", "bottom"]].set_visible(False)
        axis.set_title(f"Candidatos para continuar «{tail_of(self.context)}»", fontsize=14, loc="left")
        axis.legend(handles=[Patch(facecolor=MODEL_COLOR, edgecolor="#9fb6bd", label="probabilidade do modelo"),
                             Patch(facecolor=CHOICE_COLOR, label="usada na escolha (temperatura, top-p)")],
                    loc="lower right", fontsize=11, frameon=False)

    def _render_panel(self) -> None:
        step = self.step
        kept_text = ""
        if step and step.options:
            _, kept = selection_distribution(step, self.temperature.val, self.top_p.val)
            kept_text = f"Mantidos pelo top-p: {int(kept.sum())} de {len(kept)}"
        self.panel.set_text(
            f"Fonte: {step.source if step else 'sem dados'}\n"
            f"Temperatura: {decimal(self.temperature.val, 1)}   ·   Top-p: {decimal(self.top_p.val, 2)}\n{kept_text}"
        )

    def render(self) -> None:
        """Redraw sentence, candidate bars, settings panel and status line."""
        self._render_sentence()
        self._render_bars()
        self._render_panel()
        self.status.set_text(self.message)
        self.figure.canvas.draw_idle()


def create_source() -> NextTokenSource:
    """Prefer the live model; keep the recording as fallback and offline mode."""
    try:
        recorded = RecordedNextTokenSource()
    except NextTokenUnavailable:
        recorded = None
    live = LiveNextTokenSource() if lm_studio.is_model_available(lm_studio.TEXT_MODEL) else None
    if live is None and recorded is None:
        raise SystemExit("Sem LM Studio e sem gravação: inicia o LM Studio com o modelo "
                         f"{lm_studio.TEXT_MODEL} ou corre com --gravar quando estiver disponível.")
    if recorded is None:
        return live
    return FallbackNextTokenSource(live, recorded)


def record_from_live_model() -> None:
    """Refresh the recording used when LM Studio is not available."""
    if not lm_studio.is_model_available(lm_studio.TEXT_MODEL):
        raise SystemExit(f"Para gravar é preciso o LM Studio com o modelo {lm_studio.TEXT_MODEL}.")
    steps = record_contexts(LiveNextTokenSource(), CONTEXTS, MAX_NEW_TOKENS)
    save_recording(steps, lm_studio.TEXT_MODEL)
    print(f"Gravados {len(steps)} contextos com o modelo {lm_studio.TEXT_MODEL}.")


def show_next_token() -> None:
    """Open the interactive window, or run a short smoke demonstration headless."""
    is_headless = os.environ.get("FORMACAO_ML_NO_PAUSE") == "1"
    interface = NextTokenInterface(RecordedNextTokenSource() if is_headless else create_source())
    try:
        if is_headless:
            for _ in range(3):
                interface.choose_greedy()
            print(f"Texto: {interface.context}")
        else:
            plt.show()
    finally:
        plt.close(interface.figure)


def main() -> None:
    """Run the exercise, or record live answers with --gravar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gravar", action="store_true", help="grava as respostas do LM Studio para uso offline")
    if parser.parse_args().gravar:
        record_from_live_model()
    else:
        show_next_token()


if __name__ == "__main__":
    main()
