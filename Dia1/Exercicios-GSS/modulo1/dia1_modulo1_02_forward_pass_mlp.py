"""Exercise 2: follow one digit through the forward pass of an untrained MLP."""

from __future__ import annotations

from dataclasses import dataclass
import os

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from apoio.digit_dataset import load_binary_demo_examples
from apoio.forward_pass_ui import ForwardPassInterface

FloatArray = NDArray[np.float64]
SEED = 23
HIDDEN_UNITS = 32


@dataclass(frozen=True)
class ForwardPass:
    """Every intermediate value of one forward pass, for inspection."""

    inputs: FloatArray
    hidden_sums: FloatArray
    hidden_activations: FloatArray
    scores: FloatArray
    probabilities: FloatArray


def init_weights(
    seed: int = SEED,
    hidden_units: int = HIDDEN_UNITS,
) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray]:
    """Return random (not trained) weights and zero biases for 64 -> hidden -> 10."""
    random = np.random.default_rng(seed)
    hidden_weights = random.normal(0.0, np.sqrt(2.0 / 64), (hidden_units, 64))
    output_weights = random.normal(0.0, np.sqrt(2.0 / hidden_units), (10, hidden_units))
    return hidden_weights, np.zeros(hidden_units), output_weights, np.zeros(10)


def softmax(scores: FloatArray) -> FloatArray:
    """Turn raw scores into probabilities, stable for large values."""
    shifted = np.exp(scores - scores.max())
    return shifted / shifted.sum()


def forward(
    image: FloatArray,
    hidden_weights: FloatArray,
    hidden_bias: FloatArray,
    output_weights: FloatArray,
    output_bias: FloatArray,
) -> ForwardPass:
    """Run pixels -> weighted sums + bias -> ReLU -> scores -> softmax."""
    if image.shape != (8, 8):
        raise ValueError("A imagem deve ter 8x8 pixels.")
    inputs = image.reshape(64) / 16.0
    hidden_sums = hidden_weights @ inputs + hidden_bias
    hidden_activations = np.maximum(hidden_sums, 0.0)
    scores = output_weights @ hidden_activations + output_bias
    return ForwardPass(inputs, hidden_sums, hidden_activations, scores, softmax(scores))


def single_neuron(
    inputs: FloatArray,
    weights: FloatArray,
    bias: float,
) -> tuple[float, float]:
    """Compute one neuron by hand: sum(weight_i * input_i) + bias, then ReLU."""
    total = sum(weight * value for weight, value in zip(weights, inputs)) + bias
    return total, max(total, 0.0)


def load_demo_examples() -> tuple[FloatArray, NDArray[np.int64]]:
    """Select only official training examples, alternating digits 5 and 0."""
    return load_binary_demo_examples()


def show_forward_pass() -> None:
    """Open the staged GUI, or complete one pass without opening a window."""
    is_headless = os.environ.get("FORMACAO_ML_NO_PAUSE") == "1"
    interface = ForwardPassInterface(*load_demo_examples(), animate=not is_headless)
    try:
        if is_headless:
            for _ in range(9):
                interface.advance()
            result = interface.demo.result
            assert result is not None
            print(f"Rede 2–2–2 sem treino. Probabilidades (0, 5): {result.probabilities}")
        else:
            plt.show()
    finally:
        interface.timer.stop()
        plt.close(interface.figure)


def main() -> None:
    show_forward_pass()


if __name__ == "__main__":
    main()
