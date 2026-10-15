"""Next-token candidates from a real model, and the sampling rules applied to them."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

from . import lm_studio

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]
TOP_CANDIDATES = 10
RECORDING_PATH = (Path(__file__).resolve().parents[1] / "respostas_gravadas") / "proximo_token.json"
CONTINUATION_MESSAGES = (
    {"role": "system", "content": "Continua o texto do assistente com a palavra seguinte, em português europeu."},
    {"role": "user", "content": "Escreve uma frase curta sobre uma ocorrência numa linha de produção."},
)


@dataclass(frozen=True)
class TokenOption:
    """One candidate continuation and the probability the model assigned to it."""

    text: str
    probability: float


@dataclass(frozen=True)
class NextTokenStep:
    """Model output for one context: ranked candidates, or the end of the text."""

    context: str
    options: tuple[TokenOption, ...]
    is_end: bool
    source: str

    @property
    def other_probability(self) -> float:
        """Probability left for every token outside the listed candidates."""
        return max(0.0, 1.0 - sum(option.probability for option in self.options))


class NextTokenUnavailable(LookupError):
    """No live model and no recording exist for the requested context."""


class NextTokenSource(Protocol):
    """Anything that returns the next-token step for a context."""

    def fetch(self, context: str) -> NextTokenStep: ...


def parse_choice(context: str, choice: dict[str, Any], source: str) -> NextTokenStep:
    """Convert an LM Studio chat choice into ranked, displayable candidates."""
    logprobs = choice.get("logprobs") or {}
    content = logprobs.get("content") or ()
    if not content:
        if choice.get("finish_reason") == "stop":
            return NextTokenStep(context, (), True, source)
        raise lm_studio.LmStudioError("O modelo não devolveu probabilidades para o próximo token.")
    options = []
    for candidate in content[0].get("top_logprobs", ()):
        text = decode_candidate(candidate)
        # Byte fragments of one character cannot be shown or appended alone; they stay in «outros».
        if text is not None:
            options.append(TokenOption(text, math.exp(float(candidate["logprob"]))))
    # The server lists its own sampled token first; the presentation ranks by probability.
    options.sort(key=lambda option: option.probability, reverse=True)
    return NextTokenStep(context, tuple(options), False, source)


def decode_candidate(candidate: dict[str, Any]) -> str | None:
    """Return the candidate text, or None when it is an incomplete UTF-8 fragment."""
    raw = candidate.get("bytes")
    if raw is None:
        return str(candidate.get("token", "")) or None
    try:
        return bytes(raw).decode("utf-8") or None
    except UnicodeDecodeError:
        return None


class LiveNextTokenSource:
    """Ask the local model for its most likely next tokens, memoizing each context."""

    def __init__(self, model: str = lm_studio.TEXT_MODEL, top_candidates: int = TOP_CANDIDATES) -> None:
        self.model = model
        self.top_candidates = top_candidates
        # Repeated calls can differ slightly; the memo keeps the screen consistent in a session.
        self.memo: dict[str, NextTokenStep] = {}

    def fetch(self, context: str) -> NextTokenStep:
        if context not in self.memo:
            messages = [*CONTINUATION_MESSAGES, {"role": "assistant", "content": context}]
            choice = lm_studio.request_chat(
                messages, self.model, timeout=30.0, max_tokens=1, temperature=0,
                logprobs=True, top_logprobs=self.top_candidates,
            )
            self.memo[context] = parse_choice(context, choice, "ao vivo")
        return self.memo[context]


class RecordedNextTokenSource:
    """Replay steps previously recorded from the live model."""

    def __init__(self, path: Path = RECORDING_PATH) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise NextTokenUnavailable(f"Gravação de próximo token ilegível: {path}") from error
        self.model = str(data["model"])
        self.recorded_on = str(data["recorded_on"])
        self.steps = {
            context: NextTokenStep(
                context,
                tuple(TokenOption(text, float(probability)) for text, probability in step["options"]),
                bool(step["is_end"]),
                f"gravado em {self.recorded_on}",
            )
            for context, step in data["steps"].items()
        }

    def fetch(self, context: str) -> NextTokenStep:
        if context not in self.steps:
            raise NextTokenUnavailable("Não há gravação para este contexto.")
        return self.steps[context]


class FallbackNextTokenSource:
    """Use the live model and switch to the recording when the server fails."""

    def __init__(self, live: NextTokenSource | None, recorded: NextTokenSource) -> None:
        self.live = live
        self.recorded = recorded

    def fetch(self, context: str) -> NextTokenStep:
        if self.live is not None:
            try:
                return self.live.fetch(context)
            except lm_studio.LmStudioError:
                self.live = None
        return self.recorded.fetch(context)


def apply_temperature(probabilities: FloatArray, temperature: float) -> FloatArray:
    """Rescale candidate probabilities as p^(1/T) and renormalize over the candidates."""
    if temperature <= 0 or not math.isfinite(temperature):
        raise ValueError("A temperatura deve ser um número positivo.")
    if probabilities.ndim != 1 or len(probabilities) == 0 or np.any(probabilities <= 0):
        raise ValueError("São necessárias probabilidades positivas para pelo menos um candidato.")
    scaled = np.exp(np.log(probabilities) / temperature - np.max(np.log(probabilities) / temperature))
    return scaled / scaled.sum()


def apply_top_p(probabilities: FloatArray, top_p: float) -> BoolArray:
    """Keep the smallest set of most likely candidates whose total reaches top_p."""
    if not 0 < top_p <= 1:
        raise ValueError("O top-p deve estar entre 0 (exclusive) e 1.")
    order = np.argsort(-probabilities, kind="stable")
    cumulative = np.cumsum(probabilities[order])
    # Small tolerance so top_p=1 keeps every candidate despite rounding.
    kept_count = int(np.searchsorted(cumulative, top_p - 1e-9) + 1)
    kept = np.zeros(len(probabilities), dtype=bool)
    kept[order[:kept_count]] = True
    return kept


def selection_distribution(step: NextTokenStep, temperature: float, top_p: float) -> tuple[FloatArray, BoolArray]:
    """Return the distribution used to choose among the listed candidates, and the kept mask."""
    probabilities = np.array([option.probability for option in step.options], dtype=np.float64)
    tempered = apply_temperature(probabilities, temperature)
    kept = apply_top_p(tempered, top_p)
    chosen = np.where(kept, tempered, 0.0)
    return chosen / chosen.sum(), kept


def choose_most_likely(step: NextTokenStep) -> int:
    """Index of the candidate with the highest model probability (greedy decoding)."""
    if not step.options:
        raise ValueError("Não há candidatos: o modelo terminou o texto.")
    return 0


def sample_candidate(step: NextTokenStep, temperature: float, top_p: float, random: np.random.Generator) -> int:
    """Draw one candidate index from the temperature/top-p adjusted distribution."""
    if not step.options:
        raise ValueError("Não há candidatos: o modelo terminou o texto.")
    distribution, _ = selection_distribution(step, temperature, top_p)
    return int(random.choice(len(distribution), p=distribution))


def record_contexts(source: NextTokenSource, contexts: tuple[str, ...], max_tokens: int,
                    branch_steps: int = 3, branch_width: int = 3) -> dict[str, NextTokenStep]:
    """Record the greedy path of each context plus greedy paths after early alternatives."""
    recorded: dict[str, NextTokenStep] = {}
    for context in contexts:
        greedy_path = _record_greedy_path(source, context, max_tokens, recorded)
        for depth, prefix in enumerate(greedy_path[:branch_steps]):
            step = recorded[prefix]
            for option in step.options[1:branch_width]:
                _record_greedy_path(source, prefix + option.text, max_tokens - depth - 1, recorded)
    return recorded


def _record_greedy_path(source: NextTokenSource, context: str, max_tokens: int,
                        recorded: dict[str, NextTokenStep]) -> list[str]:
    path = []
    for _ in range(max(0, max_tokens) + 1):
        step = recorded.setdefault(context, source.fetch(context))
        path.append(context)
        if step.is_end or not step.options:
            break
        context += step.options[0].text
    return path


def save_recording(steps: dict[str, NextTokenStep], model: str, path: Path = RECORDING_PATH) -> None:
    """Write recorded steps as UTF-8 JSON with the model and date for traceability."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "model": model,
        "recorded_on": date.today().isoformat(),
        "note": "Probabilidades devolvidas pelo LM Studio (top_logprobs) para cada contexto.",
        "steps": {
            context: {"is_end": step.is_end, "options": [[o.text, round(o.probability, 6)] for o in step.options]}
            for context, step in steps.items()
        },
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
