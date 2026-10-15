"""Didactic WordPiece tokenizer shared by the slides and exercise 01."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

VOCABULARY_PATH = Path(__file__).with_name("vocabulario_didatico.json")
UNKNOWN = "[UNK]"
CONTINUATION = "##"


@dataclass(frozen=True)
class Token:
    """One piece of the text, its vocabulary ID and the word it came from."""

    piece: str
    token_id: int
    word_index: int

    @property
    def is_unknown(self) -> bool:
        return self.piece == UNKNOWN


def load_vocabulary(path: Path = VOCABULARY_PATH) -> dict[str, int]:
    """Read the piece → ID table and check that IDs are unique."""
    try:
        pieces = json.loads(path.read_text(encoding="utf-8"))["pecas"]
    except (OSError, json.JSONDecodeError, KeyError) as error:
        raise ValueError(f"Vocabulário didático ilegível: {path}") from error
    if UNKNOWN not in pieces or len(set(pieces.values())) != len(pieces):
        raise ValueError(f"O vocabulário tem de conter {UNKNOWN} e IDs únicos: {path}")
    return {str(piece): int(token_id) for piece, token_id in pieces.items()}


def split_words(text: str) -> list[str]:
    """Pre-tokenize into words and single punctuation marks (case is kept)."""
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def split_word(word: str, vocabulary: dict[str, int]) -> list[str]:
    """Greedy longest-match WordPiece: the largest known piece first, ## for continuations."""
    pieces, start = [], 0
    while start < len(word):
        prefix = CONTINUATION if start else ""
        end = next((end for end in range(len(word), start, -1) if prefix + word[start:end] in vocabulary), None)
        if end is None:
            # As in WordPiece, a word that cannot be fully written with known pieces becomes [UNK].
            return [UNKNOWN]
        pieces.append(prefix + word[start:end])
        start = end
    return pieces


def tokenize(text: str, vocabulary: dict[str, int]) -> list[Token]:
    """Split a text into vocabulary pieces with their IDs."""
    return [Token(piece, vocabulary[piece], index)
            for index, word in enumerate(split_words(text))
            for piece in split_word(word, vocabulary)]
