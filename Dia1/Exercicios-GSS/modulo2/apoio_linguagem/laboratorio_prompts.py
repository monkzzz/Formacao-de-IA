"""Prompts, references and model runners for the prompt laboratory (exercise 05)."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import date
from itertools import product
from pathlib import Path
from typing import Protocol

from . import lm_studio

RECORDING_PATH = (Path(__file__).resolve().parents[1] / "respostas_gravadas") / "laboratorio_prompts.json"
OCCURRENCE = ("A linha 2 parou às 10h15 devido a uma falha no sensor. "
              "A produção foi retomada às 10h35 após a substituição do sensor.")
CASES = {"simples": "Sensor sem sinal.", "ambíguo": "Sensor sem sinal após impacto. A peça apresenta fissura."}
EXAMPLES = ("Sensor avariado: Manutenção", "Peça com fissura: Qualidade", "Entrega atrasada: Logística")
INSTRUCTION = "Classifica a ocorrência em Manutenção, Qualidade ou Logística. Devolve apenas a categoria."
PRIORITY_RULE = " Se houver vários indícios, dano físico da peça tem prioridade."
TASKS = ("Classificar", "Resumir", "Extrair")
EXAMPLE_COUNTS = (0, 1, 3)
TEMPERATURES = (0.0, 0.7, 1.2)
MAX_TOKENS = (120, 8)
REPETITIONS = 3


@dataclass(frozen=True)
class PromptSetup:
    """What the trainer selected: task, case, number of examples and the priority rule."""

    task: str = "Classificar"
    case: str = "ambíguo"
    examples: int = 0
    with_rule: bool = False


@dataclass(frozen=True)
class Answer:
    """One model answer with the information needed to discuss it."""

    text: str
    finish_reason: str
    prompt_tokens: int
    completion_tokens: int
    seconds: float
    source: str


def build_prompt(setup: PromptSetup) -> str:
    """Exact text sent to the model for the selected setup."""
    if setup.task == "Resumir":
        return f"Resume a ocorrência numa frase. Usa apenas informação do texto.\nOcorrência: {OCCURRENCE}"
    if setup.task == "Extrair":
        return ("Extrai linha, hora de paragem, hora de retoma e duração em minutos. "
                f"Se um campo faltar, indica não informado.\nOcorrência: {OCCURRENCE}")
    if setup.task != "Classificar" or setup.case not in CASES or setup.examples not in EXAMPLE_COUNTS:
        raise ValueError(f"Configuração de prompt inválida: {setup}")
    instruction = INSTRUCTION + (PRIORITY_RULE if setup.with_rule else "")
    examples = "\n".join(EXAMPLES[:setup.examples])
    return instruction + (f"\n\nExemplos:\n{examples}" if setup.examples else "") + f"\n\nOcorrência: {CASES[setup.case]}"


def reference_for(setup: PromptSetup) -> str:
    """Prepared reference used to score the answer (didactic criteria)."""
    if setup.task == "Resumir":
        return "Falha no sensor da linha 2 e retoma após a substituição (sem causas acrescentadas)."
    if setup.task == "Extrair":
        return "Linha 2 · paragem 10h15 · retoma 10h35 · 20 minutos."
    if setup.case == "simples":
        return "Manutenção."
    if setup.with_rule:
        return "Qualidade (pela regra: dano físico da peça tem prioridade)."
    return "Ambíguo: há sensor (Manutenção) e fissura (Qualidade); falta um critério."


def recording_key(prompt: str, temperature: float, max_tokens: int, repetition: int) -> str:
    """Stable key of one recorded call."""
    return f"{temperature:.1f}|{max_tokens}|{repetition}|{prompt}"


class PromptRunner(Protocol):
    """Anything that answers a prompt (live model or recording)."""

    def run(self, prompt: str, temperature: float, max_tokens: int, repetition: int) -> Answer: ...


class LivePromptRunner:
    """Send the prompt to the AMALIA model in LM Studio."""

    def run(self, prompt: str, temperature: float, max_tokens: int, repetition: int) -> Answer:
        start = time.perf_counter()
        choice = lm_studio.request_chat([{"role": "user", "content": prompt}], timeout=120.0,
                                        temperature=temperature, max_tokens=max_tokens)
        usage = choice["usage"]
        return Answer(choice["message"]["content"].strip(), choice["finish_reason"],
                      int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0)),
                      round(time.perf_counter() - start, 1), "ao vivo")


class RecordedPromptRunner:
    """Replay answers recorded from the live model."""

    def __init__(self, path: Path = RECORDING_PATH) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise lm_studio.LmStudioError(f"Gravação do laboratório ilegível: {path}") from error
        self.recorded_on = data["data"]
        self.answers = data["respostas"]

    def run(self, prompt: str, temperature: float, max_tokens: int, repetition: int) -> Answer:
        key = recording_key(prompt, temperature, max_tokens, repetition)
        if key not in self.answers:
            raise lm_studio.LmStudioError("Sem resposta gravada para esta combinação.")
        return Answer(**{**self.answers[key], "source": f"gravado em {self.recorded_on}"})


class FallbackPromptRunner:
    """Use the live model and switch to the recording if the server fails."""

    def __init__(self, live: PromptRunner | None, recorded: PromptRunner | None) -> None:
        self.live, self.recorded = live, recorded

    def run(self, prompt: str, temperature: float, max_tokens: int, repetition: int) -> Answer:
        if self.live is not None:
            try:
                return self.live.run(prompt, temperature, max_tokens, repetition)
            except lm_studio.LmStudioError:
                self.live = None
        if self.recorded is None:
            raise lm_studio.LmStudioError("LM Studio indisponível e sem gravação.")
        return self.recorded.run(prompt, temperature, max_tokens, repetition)


def all_setups() -> list[PromptSetup]:
    """Every setup the interface can produce."""
    classification = [PromptSetup("Classificar", case, examples, rule)
                      for case, examples, rule in product(CASES, EXAMPLE_COUNTS, (False, True))]
    return classification + [PromptSetup("Resumir"), PromptSetup("Extrair")]


def record_all(runner: PromptRunner, path: Path = RECORDING_PATH) -> int:
    """Record every setup, temperature, token limit and repetition for offline use."""
    answers = {}
    for setup, temperature, max_tokens, repetition in product(all_setups(), TEMPERATURES, MAX_TOKENS,
                                                               range(REPETITIONS)):
        prompt = build_prompt(setup)
        answer = runner.run(prompt, temperature, max_tokens, repetition)
        answers[recording_key(prompt, temperature, max_tokens, repetition)] = {
            key: value for key, value in asdict(answer).items() if key != "source"}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"modelo": lm_studio.TEXT_MODEL, "data": date.today().isoformat(),
                                "respostas": answers}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(answers)
