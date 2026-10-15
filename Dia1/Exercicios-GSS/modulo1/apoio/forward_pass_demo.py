"""Deterministic calculations and presentation state for a two-input forward pass."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
LabelArray = NDArray[np.int64]
SEED = 23
CLASSES = (0, 5)
DEFAULT_PIXELS = (2, 10)


class Stage(IntEnum):
    """The presenter reveals values only after the corresponding computation."""

    IMAGE = 0
    MATRIX = 1
    FLATTEN = 2
    INPUTS = 3
    PARAMETERS = 4
    HIDDEN_ONE = 5
    HIDDEN_TWO = 6
    SCORES = 7
    SOFTMAX = 8
    RESULT = 9


@dataclass(frozen=True)
class DemoParameters:
    """Two dense layers, each with two units and a separate bias per unit."""

    hidden_weights: FloatArray
    hidden_bias: FloatArray
    output_weights: FloatArray
    output_bias: FloatArray


@dataclass(frozen=True)
class DemoResult:
    """Exact contributions, intermediate sums and final probabilities."""

    inputs: FloatArray
    hidden_contributions: FloatArray
    hidden_sums: FloatArray
    hidden_activations: FloatArray
    output_contributions: FloatArray
    scores: FloatArray
    probabilities: FloatArray


def flatten_image(image: FloatArray) -> FloatArray:
    """Keep row-major order and normalize all 64 UCI intensities by 16."""
    if image.shape != (8, 8) or not np.isfinite(image).all():
        raise ValueError("A imagem deve ser uma matriz 8×8 com valores finitos.")
    if np.any((image < 0) | (image > 16)):
        raise ValueError("As intensidades UCI devem estar entre 0 e 16.")
    return image.reshape(64).copy() / 16.0


def initialize_parameters(seed: int = SEED) -> DemoParameters:
    """Randomize weights AND biases; use two decimals as actual teaching values."""
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("A seed deve ser um inteiro não negativo.")
    random = np.random.default_rng(seed)
    arrays = [np.round(random.uniform(-1, 1, shape), 2) for shape in ((2, 2), 2, (2, 2), 2)]
    # Fixed two-decimal parameters keep visible arithmetic faithful to the model.
    for array in arrays:
        array.setflags(write=False)
    return DemoParameters(*arrays)


def run_forward(inputs: FloatArray, parameters: DemoParameters) -> DemoResult:
    """Compute one 2–2–2 pass without learning or modifying any parameter."""
    if inputs.shape != (2,) or not np.isfinite(inputs).all():
        raise ValueError("São necessárias duas entradas finitas.")
    for values, shape in ((parameters.hidden_weights, (2, 2)), (parameters.hidden_bias, (2,)),
                          (parameters.output_weights, (2, 2)), (parameters.output_bias, (2,))):
        if values.shape != shape or not np.isfinite(values).all():
            raise ValueError(f"Parâmetros inválidos: esperada a forma {shape} e valores finitos.")
    hidden_contributions = parameters.hidden_weights * inputs
    hidden_sums = hidden_contributions.sum(axis=1) + parameters.hidden_bias
    activations = np.maximum(hidden_sums, 0.0)
    output_contributions = parameters.output_weights * activations
    scores = output_contributions.sum(axis=1) + parameters.output_bias
    exponentials = np.exp(scores - scores.max())
    return DemoResult(inputs.copy(), hidden_contributions, hidden_sums, activations,
                      output_contributions, scores, exponentials / exponentials.sum())


class ForwardDemo:
    """Navigate an untrained network while keeping inputs and parameters independent."""

    def __init__(self, images: FloatArray, labels: LabelArray) -> None:
        if images.ndim != 3 or images.shape[1:] != (8, 8) or not len(images):
            raise ValueError("São necessárias imagens de demonstração 8×8.")
        if labels.shape != (len(images),) or not np.isin(labels, CLASSES).all():
            raise ValueError("Cada imagem deve ter um label 0 ou 5.")
        for image in images:
            flatten_image(image)
        self.images, self.labels = images.copy(), labels.copy()
        self.reset()

    @property
    def image(self) -> FloatArray:
        """Return the current raw 8×8 image."""
        return self.images[self.example_index]

    @property
    def vector(self) -> FloatArray:
        """Return the full normalized vector before selecting the two inputs."""
        return flatten_image(self.image)

    @property
    def inputs(self) -> FloatArray:
        """Select two distinct pixels; this deliberately loses the other 62 values."""
        return self.vector[list(self.pixel_indices)]

    def reset(self) -> None:
        """Restore the first digit, default pixels and initial random seed."""
        self.stage = Stage.IMAGE
        self.seed = SEED
        self.example_index = 0
        self.pixel_indices = DEFAULT_PIXELS
        self.parameters: DemoParameters | None = None
        self.result: DemoResult | None = None

    def advance(self) -> None:
        """Reveal the next stage, initializing or computing exactly when needed."""
        self.stage = Stage(min(int(Stage.RESULT), int(self.stage) + 1))
        if self.stage >= Stage.PARAMETERS and self.parameters is None:
            self.parameters = initialize_parameters(self.seed)
        if self.stage >= Stage.HIDDEN_ONE and self.result is None:
            assert self.parameters is not None
            self.result = run_forward(self.inputs, self.parameters)

    def go_back(self) -> None:
        """Revisit a stage without reinitializing the network."""
        self.stage = Stage(max(0, int(self.stage) - 1))

    def select_pixel(self, slot: int, index: int) -> None:
        """Replace one input and invalidate its pass, retaining the fixed parameters."""
        if slot not in (0, 1) or not isinstance(index, int) or not 0 <= index < 64:
            raise ValueError("Escolhe a entrada 1 ou 2 e um dos 64 píxeis.")
        if index == self.pixel_indices[1 - slot]:
            raise ValueError("As duas entradas devem usar píxeis diferentes.")
        indices = list(self.pixel_indices)
        indices[slot] = index
        self.pixel_indices = tuple(indices)
        self.result = None
        self.stage = Stage.INPUTS

    def randomize(self) -> None:
        """Show a fresh reproducible initialization, never treating it as training."""
        self.seed += 1
        self.parameters = initialize_parameters(self.seed)
        self.result = None
        self.stage = Stage.PARAMETERS

    def next_example(self) -> None:
        """Change the image while retaining parameters for a fair input comparison."""
        self.example_index = (self.example_index + 1) % len(self.images)
        self.result = None
        self.stage = Stage.IMAGE
