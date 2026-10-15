"""Exercise 1: split a sentence into tokens and IDs with a didactic WordPiece vocabulary."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from matplotlib.backend_bases import MouseEvent
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import TextBox

from apoio_linguagem import lm_studio
from apoio_linguagem.interface_base import (
    BLUE, BOX_LINE, INK, MUTED, RED, STATUS, TEAL, add_buttons, add_footer, create_window, run_window,
)
from apoio_linguagem.tokenizador_didatico import Token, load_vocabulary, split_words, tokenize

EXAMPLES = (
    ("peça parou / partiu", "A peça parou e a peça partiu."),
    ("linha 2 às 10h15", "A linha 2 parou às 10h15."),
    ("produção retomada", "A produção foi retomada após a substituição do sensor."),
    ("palavras novas", "Rolamento sobreaquecido!"),
)
COUNTS_PATH = Path(__file__).with_name("respostas_gravadas") / "contagem_tokens.json"
WORD_COLORS = ("#e1eff2", "#e8f3e1", "#f3eadf", "#ece4f3", "#e0ebf6", "#f6e3ea")
UNKNOWN_FILL = "#f6d5d1"
TOKEN_ROWS = (0.70, 0.25)  # the token area has room for two rows of chips and their IDs


def load_recorded_counts(path: Path = COUNTS_PATH) -> dict[str, int]:
    """AMALIA token counts recorded for the prepared sentences."""
    try:
        return {text: int(count) for text, count in json.loads(path.read_text(encoding="utf-8"))["contagens"].items()}
    except (OSError, json.JSONDecodeError, KeyError):
        return {}


def describe(tokens: list[Token], text: str) -> str:
    """One-line summary: words, tokens, repeated pieces and unknown words."""
    repeated = [f"{piece} ({tokens[[t.piece for t in tokens].index(piece)].token_id}) ×{count}"
                for piece, count in Counter(t.piece for t in tokens).items() if count > 1 and piece != "[UNK]"]
    unknown = sum(token.is_unknown for token in tokens)
    parts = [f"{len(split_words(text))} palavras e sinais → {len(tokens)} tokens"]
    if repeated:
        parts.append("mesma peça, mesmo ID: " + ", ".join(repeated))
    if unknown:
        parts.append(f"{unknown} palavra(s) sem peças conhecidas → [UNK]")
    return "  ·  ".join(parts)


class TokenInterface:
    """Type or choose a sentence and see its pieces, IDs and the real model's count."""

    def __init__(self, vocabulary: dict[str, int], live_counts: bool) -> None:
        self.vocabulary = vocabulary
        self.live_counts = live_counts
        self.recorded_counts = load_recorded_counts()
        self.text = EXAMPLES[0][1]
        self.model_count = "clica em «Contar no AMALIA» para comparar com o modelo real"
        self.show_vocabulary = False
        self.figure = create_window("Tokens e IDs", "Tokens e IDs: do texto aos números",
                                    "Escreve uma frase ou escolhe um exemplo. Cada palavra é partida nas maiores "
                                    "peças que existem no vocabulário.")
        self.textbox = TextBox(self.figure.add_axes((0.11, 0.80, 0.84, 0.06)), "Texto: ", initial=self.text,
                               color="white", hovercolor="#f2f8f9")
        self.textbox.label.set_fontsize(15)
        self.textbox.text_disp.set_fontsize(16)
        self.textbox.text_disp.set_clip_on(True)  # long sentences stay inside the box instead of the window
        self.textbox.on_submit(self.set_text)
        self.example_buttons = add_buttons(self.figure, [
            (label, lambda event, sentence=sentence: self.choose_example(sentence)) for label, sentence in EXAMPLES
        ], y=0.715, width=0.2, gap=0.0267)
        self.axis = self.figure.add_axes((0.05, 0.30, 0.90, 0.38))
        self.summary = self.figure.text(0.05, 0.245, "", fontsize=14, color=INK)
        self.model_line = self.figure.text(0.05, 0.195, "", fontsize=14, color=STATUS)
        self.buttons = add_buttons(self.figure, [
            ("Contar no AMALIA", self.count_in_model), ("Ver vocabulário", self.toggle_vocabulary),
            ("Limpar", self.clear),
        ])
        add_footer(self.figure, f"Vocabulário didático com {len(vocabulary)} peças (um modelo real tem dezenas de "
                                "milhares) · ## = continuação da palavra · [UNK] = sem peças conhecidas")
        self.render()

    def set_text(self, text: str) -> None:
        """Tokenize new text typed in the box (Enter)."""
        self.text = text.strip()
        self.model_count = "clica em «Contar no AMALIA» para comparar com o modelo real"
        self.show_vocabulary = False
        self.render()

    def choose_example(self, sentence: str) -> None:
        """Load a prepared sentence into the box and tokenize it."""
        self.textbox.set_val(sentence)  # triggers on_change only; on_submit is called explicitly
        self.set_text(sentence)

    def clear(self, event: MouseEvent | None = None) -> None:
        self.textbox.set_val("")
        self.set_text("")

    def toggle_vocabulary(self, event: MouseEvent | None = None) -> None:
        """Switch between the tokens of the text and the whole didactic vocabulary."""
        self.show_vocabulary = not self.show_vocabulary
        self.render()

    def count_in_model(self, event: MouseEvent | None = None) -> None:
        """Ask the real model how many tokens the same text uses (or use the recording)."""
        if not self.text:
            return
        try:
            if not self.live_counts:
                raise lm_studio.LmStudioError("modo gravado")
            count, source = lm_studio.count_tokens(self.text), "ao vivo"
        except lm_studio.LmStudioError:
            if self.text not in self.recorded_counts:
                self.model_count = "LM Studio indisponível e sem contagem gravada para este texto."
                self.render()
                return
            count, source = self.recorded_counts[self.text], "gravado"
        didactic = len(tokenize(self.text, self.vocabulary))
        self.model_count = f"AMALIA: {count} tokens ({source})  ·  vocabulário didático: {didactic} tokens"
        self.render()

    def _draw_chip(self, x: float, y: float, width: float, token: Token, color: str, repeated: bool) -> None:
        axis = self.axis
        fill, text_color = (UNKNOWN_FILL, RED) if token.is_unknown else (color, INK)
        axis.add_patch(FancyBboxPatch((x, y), width, 0.16, boxstyle="round,pad=0,rounding_size=0.015",
                                      facecolor=fill, edgecolor=BLUE if repeated else BOX_LINE,
                                      linewidth=2.5 if repeated else 1, transform=axis.transAxes, clip_on=False))
        axis.text(x + width / 2, y + 0.08, token.piece, ha="center", va="center", fontsize=18, color=text_color,
                  transform=axis.transAxes)
        axis.text(x + width / 2, y - 0.07, str(token.token_id), ha="center", va="center", fontsize=16,
                  color=TEAL if repeated else INK, weight="bold" if repeated else "normal", transform=axis.transAxes)

    def _render_tokens(self) -> None:
        tokens = tokenize(self.text, self.vocabulary)
        counts = Counter(token.piece for token in tokens)
        self.axis.text(0.0, 0.94, "tokens", fontsize=13, color=MUTED, transform=self.axis.transAxes)
        self.axis.text(0.0, 0.55, "IDs ↓ por baixo de cada peça", fontsize=13, color=MUTED,
                       transform=self.axis.transAxes)
        x, row, shown = 0.0, 0, 0
        for token in tokens:
            width = 0.03 + 0.0115 * len(token.piece)
            if x + width > 1.0:
                if row + 1 == len(TOKEN_ROWS):
                    break
                x, row = 0.0, row + 1
            self._draw_chip(x, TOKEN_ROWS[row], width, token, WORD_COLORS[token.word_index % len(WORD_COLORS)],
                            counts[token.piece] > 1 and not token.is_unknown)
            x += width + 0.008
            shown += 1
        hidden = len(tokens) - shown
        if hidden:
            self.axis.text(1.0, 0.0, f"… e mais {hidden} token" + ("s" if hidden > 1 else ""), ha="right",
                           fontsize=13, color=MUTED, transform=self.axis.transAxes)
        self.summary.set_text(describe(tokens, self.text) if tokens else "Escreve um texto e carrega Enter.")

    def _render_vocabulary(self) -> None:
        entries = sorted(self.vocabulary.items(), key=lambda item: item[1])
        rows = 12
        for index, (piece, token_id) in enumerate(entries):
            column, row = divmod(index, rows)
            self.axis.text(column * 0.2, 0.95 - row * 0.08, f"{token_id:>5}  {piece}", fontsize=13,
                           family="monospace", color=RED if piece == "[UNK]" else INK, va="top",
                           transform=self.axis.transAxes)
        self.summary.set_text("O vocabulário é uma lista fixa: cada peça tem o seu ID. «Ver vocabulário» volta ao texto.")

    def render(self) -> None:
        """Redraw tokens (or the vocabulary), the summary and the model count."""
        self.axis.clear()
        self.axis.axis("off")
        if self.show_vocabulary:
            self._render_vocabulary()
        else:
            self._render_tokens()
        self.model_line.set_text(self.model_count)
        self.figure.canvas.draw_idle()


def record_counts() -> None:
    """Record the AMALIA token count of the prepared sentences for offline use."""
    if not lm_studio.is_model_available(lm_studio.TEXT_MODEL):
        raise SystemExit(f"Para gravar é preciso o LM Studio com o modelo {lm_studio.TEXT_MODEL}.")
    counts = {sentence: lm_studio.count_tokens(sentence) for _, sentence in EXAMPLES}
    COUNTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    COUNTS_PATH.write_text(json.dumps({"modelo": lm_studio.TEXT_MODEL, "data": date.today().isoformat(),
                                       "contagens": counts}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(counts)


def main() -> None:
    """Open the exercise, or record the model counts with --gravar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gravar", action="store_true", help="grava as contagens do AMALIA para uso offline")
    if parser.parse_args().gravar:
        record_counts()
        return
    live = lm_studio.is_model_available(lm_studio.TEXT_MODEL)
    interface = TokenInterface(load_vocabulary(), live_counts=live)

    def smoke() -> None:
        for _, sentence in EXAMPLES:
            interface.choose_example(sentence)
            print(interface.summary.get_text())

    run_window(interface.figure, smoke)


if __name__ == "__main__":
    main()
