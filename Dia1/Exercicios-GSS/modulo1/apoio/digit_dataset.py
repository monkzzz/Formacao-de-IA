"""Load and validate the official UCI handwritten-digit train/test split."""

from __future__ import annotations

import io
import zipfile

import numpy as np
from numpy.typing import NDArray

from .dataset_cache import load_dataset_archive

PixelArray = NDArray[np.float64]
LabelArray = NDArray[np.int64]

DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/80/"
    "optical+recognition+of+handwritten+digits.zip"
)
DIGIT_COUNT = 10


def load_digit_splits() -> tuple[PixelArray, LabelArray, PixelArray, LabelArray]:
    """Load the official train/test files without mixing their rows."""
    archive_bytes = load_dataset_archive(
        DATASET_URL,
        "optical_digits.zip",
        "formacao-gss-digits-demo/1.0",
    )
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        train_data = np.loadtxt(
            io.BytesIO(archive.read("optdigits.tra")),
            delimiter=",",
            dtype=np.int64,
        )
        test_data = np.loadtxt(
            io.BytesIO(archive.read("optdigits.tes")),
            delimiter=",",
            dtype=np.int64,
        )

    train_pixels = train_data[:, :-1].astype(np.float64).reshape(-1, 8, 8)
    train_labels = train_data[:, -1].astype(np.int64)
    test_pixels = test_data[:, :-1].astype(np.float64).reshape(-1, 8, 8)
    test_labels = test_data[:, -1].astype(np.int64)
    if train_pixels.shape[1:] != (8, 8) or test_pixels.shape[1:] != (8, 8):
        raise ValueError("Esperadas imagens UCI com 8x8 pixels.")
    if not np.isin(train_labels, np.arange(DIGIT_COUNT)).all():
        raise ValueError("O conjunto de treino contem labels fora do intervalo 0-9.")
    if not np.isin(test_labels, np.arange(DIGIT_COUNT)).all():
        raise ValueError("O conjunto de teste contem labels fora do intervalo 0-9.")
    if not train_labels.size or not test_labels.size:
        raise ValueError("Os conjuntos oficiais de treino e teste nao podem estar vazios.")
    return train_pixels, train_labels, test_pixels, test_labels


def load_binary_demo_examples() -> tuple[PixelArray, LabelArray]:
    """Select the same training-only 5/0 examples for exercises 02 and 03."""
    images, labels, _, _ = load_digit_splits()
    fives, zeros = np.flatnonzero(labels == 5), np.flatnonzero(labels == 0)
    if not len(fives) or not len(zeros):
        raise ValueError("A demonstração precisa de exemplos de treino dos dígitos 0 e 5.")
    # Reuse the training digit from slide18 when available; never select from test.
    first_five = 65 if len(labels) > 65 and labels[65] == 5 else int(fives[0])
    selected_fives = [first_five, *(int(i) for i in fives[:3] if i != first_five)]
    indices = [i for pair in zip(selected_fives, zeros[:3]) for i in pair]
    return images[indices], labels[indices]
