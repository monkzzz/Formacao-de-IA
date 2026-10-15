"""Exercise 5: change the prompt and the generation settings, ask AMALIA and compare answers."""

from __future__ import annotations

import argparse
import textwrap
from dataclasses import replace

from matplotlib.backend_bases import MouseEvent

from apoio_linguagem import lm_studio
from apoio_linguagem.interface_base import (
    INK, MUTED, ORANGE, STATUS, TEAL, add_buttons, add_footer, create_window, run_window,
)
from apoio_linguagem.laboratorio_prompts import (
    EXAMPLE_COUNTS, MAX_TOKENS, REPETITIONS, TASKS, TEMPERATURES, Answer, FallbackPromptRunner,
    LivePromptRunner, PromptRunner, PromptSetup, RecordedPromptRunner, build_prompt, record_all, reference_for,
)

CONTEXT_WINDOW = 32768
FINISH_LABELS = {"stop": "terminou sozinho", "length": "cortado pelo limite"}


def next_in(values: tuple, current: object) -> object:
    """Cycle to the value after `current`."""
    return values[(values.index(current) + 1) % len(values)]


def format_answer(index: int, answer: Answer) -> str:
    """Answer text wrapped for the panel, with its stop reason and size."""
    finish = FINISH_LABELS.get(answer.finish_reason, answer.finish_reason)
    body = textwrap.fill(f"«{answer.text}»", width=62, max_lines=4, placeholder=" …»")
    seconds = f"{answer.seconds:.1f}".replace(".", ",")
    return f"{index}. {body}\n    {finish} · {answer.completion_tokens} tokens · {seconds} s"


class PromptLabInterface:
    """Build a prompt with buttons, send it, and compare the answers with a reference."""

    def __init__(self, runner: PromptRunner) -> None:
        self.runner = runner
        self.setup = PromptSetup()
        self.temperature = TEMPERATURES[0]
        self.max_tokens = MAX_TOKENS[0]
        self.answers: list[Answer] = []
        self.message = "Escolhe a configuração e carrega em «Enviar»."
        self.figure = create_window("Laboratório de prompts", "Laboratório de prompts · AMALIA",
                                    "O mesmo modelo, pedidos diferentes. Muda uma coisa de cada vez e compara as "
                                    "respostas com a referência.")
        self.config_buttons = add_buttons(self.figure, [
            ("", self.cycle_task), ("", self.cycle_case), ("", self.cycle_examples), ("", self.toggle_rule),
            ("", self.cycle_temperature), ("", self.cycle_max_tokens),
        ], y=0.80, width=0.142, gap=0.0136)
        self.prompt_text = self.figure.text(0.05, 0.70, "", fontsize=12, family="monospace", va="top", color=INK)
        self.answers_text = self.figure.text(0.52, 0.70, "", fontsize=12.5, va="top", color=INK, linespacing=1.4)
        self.reference_text = self.figure.text(0.52, 0.27, "", fontsize=13, va="top", color=TEAL)
        self.status = self.figure.text(0.05, 0.185, "", fontsize=13.5, color=STATUS)
        self.figure.text(0.05, 0.735, "Prompt enviado", fontsize=14, weight="bold", color=TEAL)
        self.figure.text(0.52, 0.735, "Respostas", fontsize=14, weight="bold", color=TEAL)
        self.action_buttons = add_buttons(self.figure, [
            ("Enviar", self.send_once), (f"Repetir {REPETITIONS}×", self.send_repeated),
            ("Limpar respostas", self.clear_answers),
        ])
        add_footer(self.figure, f"Modelo {lm_studio.TEXT_MODEL} no LM Studio, ou respostas gravadas do mesmo "
                                "modelo · uma execução não prova uma melhoria geral")
        self.render()

    def _change(self, **changes: object) -> None:
        self.setup = replace(self.setup, **changes)
        self.answers = []
        self.render()

    def cycle_task(self, event: MouseEvent | None = None) -> None:
        self._change(task=next_in(TASKS, self.setup.task))

    def cycle_case(self, event: MouseEvent | None = None) -> None:
        self._change(case="simples" if self.setup.case == "ambíguo" else "ambíguo")

    def cycle_examples(self, event: MouseEvent | None = None) -> None:
        self._change(examples=next_in(EXAMPLE_COUNTS, self.setup.examples))

    def toggle_rule(self, event: MouseEvent | None = None) -> None:
        self._change(with_rule=not self.setup.with_rule)

    def cycle_temperature(self, event: MouseEvent | None = None) -> None:
        self.temperature = next_in(TEMPERATURES, self.temperature)
        self.answers = []
        self.render()

    def cycle_max_tokens(self, event: MouseEvent | None = None) -> None:
        self.max_tokens = next_in(MAX_TOKENS, self.max_tokens)
        self.answers = []
        self.render()

    def clear_answers(self, event: MouseEvent | None = None) -> None:
        self.answers = []
        self.message = "Respostas apagadas."
        self.render()

    def send_once(self, event: MouseEvent | None = None) -> None:
        self._send(1)

    def send_repeated(self, event: MouseEvent | None = None) -> None:
        self._send(REPETITIONS)

    def _send(self, count: int) -> None:
        self.message = "A enviar ao modelo…"
        self.render()
        self.figure.canvas.flush_events()
        prompt = build_prompt(self.setup)
        try:
            self.answers = [self.runner.run(prompt, self.temperature, self.max_tokens, repetition)
                            for repetition in range(count)]
        except lm_studio.LmStudioError as error:
            self.answers = []
            self.message = str(error)
        else:
            first = self.answers[0]
            self.message = (f"Fonte: {first.source} · pedido com {first.prompt_tokens} tokens de "
                            f"{CONTEXT_WINDOW:,} na janela".replace(",", " "))
        self.render()

    def _button_labels(self) -> tuple[str, ...]:
        is_classification = self.setup.task == "Classificar"
        return (f"Tarefa: {self.setup.task}",
                f"Caso: {self.setup.case}" if is_classification else "Caso: —",
                f"Exemplos: {self.setup.examples}" if is_classification else "Exemplos: —",
                f"Regra: {'sim' if self.setup.with_rule else 'não'}" if is_classification else "Regra: —",
                f"Temperatura: {self.temperature:.1f}".replace(".", ","),
                f"Máx. tokens: {self.max_tokens}")

    def render(self) -> None:
        """Refresh the button labels, the exact prompt, the answers and the reference."""
        for button, label in zip(self.config_buttons, self._button_labels()):
            button.label.set_text(label)
        prompt = build_prompt(self.setup)
        self.prompt_text.set_text("\n".join(textwrap.fill(line, width=58) if line else "" for line in prompt.split("\n")))
        self.answers_text.set_text("\n\n".join(format_answer(i, a) for i, a in enumerate(self.answers, start=1))
                                   or "(ainda sem respostas)")
        self.answers_text.set_color(INK if self.answers else MUTED)
        self.reference_text.set_text("Referência: " + textwrap.fill(reference_for(self.setup), width=60))
        self.status.set_text(self.message)
        self.status.set_color(ORANGE if "indisponível" in self.message or "Sem resposta" in self.message else STATUS)
        self.figure.canvas.draw_idle()


def create_runner() -> PromptRunner:
    """Live AMALIA when available, with the recording as fallback."""
    try:
        recorded = RecordedPromptRunner()
    except lm_studio.LmStudioError:
        recorded = None
    live = LivePromptRunner() if lm_studio.is_model_available(lm_studio.TEXT_MODEL) else None
    return FallbackPromptRunner(live, recorded)


def main() -> None:
    """Open the laboratory, or record every combination with --gravar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gravar", action="store_true", help="grava todas as combinações para uso offline")
    if parser.parse_args().gravar:
        if not lm_studio.is_model_available(lm_studio.TEXT_MODEL):
            raise SystemExit(f"Para gravar é preciso o LM Studio com o modelo {lm_studio.TEXT_MODEL}.")
        print(f"Gravadas {record_all(LivePromptRunner())} respostas.")
        return
    interface = PromptLabInterface(RecordedPromptRunner() if lm_studio.is_offline_forced() else create_runner())

    def smoke() -> None:
        interface.cycle_examples()
        interface.cycle_examples()
        interface.send_once()
        print(interface.answers_text.get_text().splitlines()[0])

    run_window(interface.figure, smoke)


if __name__ == "__main__":
    main()
