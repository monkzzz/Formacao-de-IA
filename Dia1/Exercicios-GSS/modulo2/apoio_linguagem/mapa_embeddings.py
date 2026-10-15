"""Phrases, embedding sources and the 2D projection for the embeddings map (exercise 02)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from . import lm_studio

FloatArray = NDArray[np.float64]
RECORDING_PATH = (Path(__file__).resolve().parents[1] / "respostas_gravadas") / "embeddings.json"
AREAS = {
    "Manutenção": ("O sensor da linha 2 avariou", "O motor sobreaqueceu e parou",
                   "Substituição do rolamento da prensa", "Fuga de óleo na máquina de corte"),
    "Qualidade": ("A peça apresenta uma fissura", "Riscos na pintura do lote 14",
                  "Medida fora da tolerância no controlo final", "Cliente devolveu peças com defeito"),
    "Logística": ("A entrega ao cliente chegou atrasada", "O camião saiu sem a carga completa",
                  "Stock de parafusos esgotado no armazém", "Encomenda enviada para a morada errada"),
    "Finanças": ("Fatura do fornecedor por pagar", "Orçamento de reparação aprovado",
                 "Pagamento recebido com atraso", "Custo da energia subiu este mês"),
}
SUGGESTIONS = ("Rolamento gasto na linha 3", "Nota de crédito emitida ao cliente", "Camião avariado na estrada",
               "Soldadura com bolhas", "A peça partiu durante o transporte")
LABELS = {
    "O sensor da linha 2 avariou": "sensor avariado", "O motor sobreaqueceu e parou": "motor sobreaquecido",
    "Substituição do rolamento da prensa": "rolamento da prensa", "Fuga de óleo na máquina de corte": "fuga de óleo",
    "A peça apresenta uma fissura": "peça com fissura", "Riscos na pintura do lote 14": "riscos na pintura",
    "Medida fora da tolerância no controlo final": "fora da tolerância",
    "Cliente devolveu peças com defeito": "peças devolvidas",
    "A entrega ao cliente chegou atrasada": "entrega atrasada", "O camião saiu sem a carga completa": "camião sem carga",
    "Stock de parafusos esgotado no armazém": "stock esgotado", "Encomenda enviada para a morada errada": "morada errada",
    "Fatura do fornecedor por pagar": "fatura por pagar", "Orçamento de reparação aprovado": "orçamento aprovado",
    "Pagamento recebido com atraso": "pagamento atrasado", "Custo da energia subiu este mês": "custo da energia",
}
BANK_SENTENCES = ("Fui ao banco levantar dinheiro.", "Sentei-me no banco do jardim.")
BANK_ANCHORS = ("conta bancária e multibanco", "parque com árvores e relva")


@dataclass(frozen=True)
class Neighbour:
    """A phrase and its cosine similarity to the selected phrase."""

    text: str
    similarity: float


class EmbeddingSource(Protocol):
    """Anything that turns texts into vectors."""

    def vectors(self, texts: list[str]) -> FloatArray: ...


def all_base_texts() -> list[str]:
    """Phrases of the four areas, in a fixed order."""
    return [text for texts in AREAS.values() for text in texts]


def area_of(text: str) -> str | None:
    """Area of a base phrase, or None for added phrases."""
    return next((area for area, texts in AREAS.items() if text in texts), None)


def normalize(vectors: FloatArray) -> FloatArray:
    """Unit-length rows, so that a dot product is the cosine similarity."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Vetor de embedding nulo.")
    return vectors / norms


class LiveEmbeddingSource:
    """Ask the embedding model in LM Studio, memoizing every text."""

    def __init__(self, model: str = lm_studio.EMBEDDING_MODEL) -> None:
        self.model = model
        self.memo: dict[str, FloatArray] = {}

    def vectors(self, texts: list[str]) -> FloatArray:
        missing = [text for text in texts if text not in self.memo]
        if missing:
            for text, vector in zip(missing, lm_studio.embed(missing, self.model)):
                self.memo[text] = np.array(vector, dtype=np.float64)
        return normalize(np.vstack([self.memo[text] for text in texts]))


class RecordedEmbeddingSource:
    """Vectors recorded from the embedding model for the prepared phrases."""

    def __init__(self, path: Path = RECORDING_PATH) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise lm_studio.LmStudioError(f"Gravação de embeddings ilegível: {path}") from error
        self.model, self.recorded_on = data["modelo"], data["data"]
        self.stored = {text: np.array(vector, dtype=np.float64) for text, vector in data["vetores"].items()}

    def vectors(self, texts: list[str]) -> FloatArray:
        missing = [text for text in texts if text not in self.stored]
        if missing:
            raise lm_studio.LmStudioError(f"Sem vetor gravado para: {missing[0]}")
        return normalize(np.vstack([self.stored[text] for text in texts]))


class FallbackEmbeddingSource:
    """Live model first; the recording if the server fails."""

    def __init__(self, live: EmbeddingSource | None, recorded: EmbeddingSource | None) -> None:
        self.live, self.recorded = live, recorded

    def vectors(self, texts: list[str]) -> FloatArray:
        if self.live is not None:
            try:
                return self.live.vectors(texts)
            except lm_studio.LmStudioError:
                self.live = None
        if self.recorded is None:
            raise lm_studio.LmStudioError("LM Studio indisponível e sem gravação.")
        return self.recorded.vectors(texts)


class Projection:
    """2D view of the vectors: the plane that best separates the mean vector of each area.

    The vectors are the model's; only the viewing plane is chosen. A plain PCA of 16 phrases is
    dominated by what all sentences share, and mixes the areas on screen even when the
    full-dimension neighbours are right.
    """

    def __init__(self, base_vectors: FloatArray, groups: list[str]) -> None:
        if len(groups) != len(base_vectors):
            raise ValueError("É preciso uma área por vetor.")
        self.mean = base_vectors.mean(axis=0)
        names = sorted(set(groups))
        centroids = np.vstack([base_vectors[[g == name for g in groups]].mean(axis=0) for name in names])
        _, _, components = np.linalg.svd(centroids - centroids.mean(axis=0), full_matrices=False)
        self.components = components[:2]

    def project(self, vectors: FloatArray) -> FloatArray:
        return (vectors - self.mean) @ self.components.T


def nearest(text: str, vector: FloatArray, texts: list[str], vectors: FloatArray, count: int = 3) -> list[Neighbour]:
    """Most similar phrases in the full embedding space (not in the 2D map)."""
    similarities = vectors @ vector
    order = [index for index in np.argsort(-similarities) if texts[index] != text]
    return [Neighbour(texts[index], float(similarities[index])) for index in order[:count]]


def same_area_rate(texts: list[str], vectors: FloatArray) -> float:
    """Share of base phrases whose nearest neighbour is in the same area (quality check)."""
    hits = [area_of(nearest(text, vector, texts, vectors, 1)[0].text) == area_of(text)
            for text, vector in zip(texts, vectors)]
    return sum(hits) / len(hits)


def record_all(source: LiveEmbeddingSource, path: Path = RECORDING_PATH) -> int:
    """Record vectors for every prepared phrase (base, suggestions and «banco»)."""
    texts = all_base_texts() + list(SUGGESTIONS) + list(BANK_SENTENCES) + list(BANK_ANCHORS)
    vectors = source.vectors(texts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "modelo": source.model, "data": date.today().isoformat(),
        "vetores": {text: [round(float(value), 5) for value in vector] for text, vector in zip(texts, vectors)},
    }, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(texts)
