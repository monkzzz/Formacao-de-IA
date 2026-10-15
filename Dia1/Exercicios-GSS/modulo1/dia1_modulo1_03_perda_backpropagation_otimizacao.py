"""Exercise 3: loss, error, backpropagation and optimisation, written by hand."""

from __future__ import annotations

from dataclasses import dataclass
import os

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from apoio.digit_dataset import load_binary_demo_examples
from apoio.learning_ui import LearningInterface

FloatArray = NDArray[np.float64]
IndexArray = NDArray[np.int64]
SEED = 23
HIDDEN_UNITS = 32
STEPS = 150


@dataclass
class Network:
    """Parameters of a 64 -> hidden ReLU -> 10 network."""

    hidden_weights: FloatArray
    hidden_bias: FloatArray
    output_weights: FloatArray
    output_bias: FloatArray


@dataclass(frozen=True)
class Gradients:
    """Gradient of the loss with respect to every parameter."""

    hidden_weights: FloatArray
    hidden_bias: FloatArray
    output_weights: FloatArray
    output_bias: FloatArray


def init_network(seed: int = SEED) -> Network:
    """Create reproducible random parameters."""
    random = np.random.default_rng(seed)
    return Network(
        random.normal(0.0, np.sqrt(2.0 / 64), (64, HIDDEN_UNITS)),
        np.zeros(HIDDEN_UNITS),
        random.normal(0.0, np.sqrt(2.0 / HIDDEN_UNITS), (HIDDEN_UNITS, 10)),
        np.zeros(10),
    )


def softmax_rows(scores: FloatArray) -> FloatArray:
    """Row-wise softmax, stable for large scores."""
    shifted = np.exp(scores - scores.max(axis=1, keepdims=True))
    return shifted / shifted.sum(axis=1, keepdims=True)


def forward(network: Network, features: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Return hidden activations and class probabilities for a batch."""
    hidden = np.maximum(features @ network.hidden_weights + network.hidden_bias, 0.0)
    return hidden, softmax_rows(hidden @ network.output_weights + network.output_bias)


def cross_entropy(probabilities: FloatArray, labels: IndexArray) -> float:
    """Mean of -log(probability given to the correct digit)."""
    correct = probabilities[np.arange(len(labels)), labels]
    return float(-np.log(np.clip(correct, 1e-12, None)).mean())


def backpropagate(
    network: Network,
    features: FloatArray,
    labels: IndexArray,
) -> tuple[float, Gradients]:
    """Return the loss and its gradients by applying the chain rule layer by layer."""
    hidden, probabilities = forward(network, features)
    loss = cross_entropy(probabilities, labels)
    # For softmax + cross-entropy, d(loss)/d(score) is (probability - one_hot) / n.
    score_error = probabilities.copy()
    score_error[np.arange(len(labels)), labels] -= 1.0
    score_error /= len(labels)
    hidden_error = (score_error @ network.output_weights.T) * (hidden > 0)
    return loss, Gradients(
        features.T @ hidden_error,
        hidden_error.sum(axis=0),
        hidden.T @ score_error,
        score_error.sum(axis=0),
    )


def gradient_descent_step(
    network: Network,
    gradients: Gradients,
    learning_rate: float,
) -> None:
    """Move every parameter a full-batch gradient step against its gradient."""
    if learning_rate <= 0:
        raise ValueError("learning_rate deve ser positivo.")
    network.hidden_weights -= learning_rate * gradients.hidden_weights
    network.hidden_bias -= learning_rate * gradients.hidden_bias
    network.output_weights -= learning_rate * gradients.output_weights
    network.output_bias -= learning_rate * gradients.output_bias


def finite_difference_check(
    network: Network,
    features: FloatArray,
    labels: IndexArray,
    epsilon: float = 1e-5,
) -> tuple[float, float]:
    """Compare one backprop gradient with a numerical slope of the loss."""
    _, gradients = backpropagate(network, features, labels)
    original = network.output_weights[0, 0]
    network.output_weights[0, 0] = original + epsilon
    upper = cross_entropy(forward(network, features)[1], labels)
    network.output_weights[0, 0] = original - epsilon
    lower = cross_entropy(forward(network, features)[1], labels)
    network.output_weights[0, 0] = original
    return float(gradients.output_weights[0, 0]), (upper - lower) / (2 * epsilon)


def train(
    features: FloatArray,
    labels: IndexArray,
    learning_rate: float,
    steps: int = STEPS,
) -> tuple[Network, list[float], list[float]]:
    """Run full-batch gradient descent; return loss and gradient norm per step."""
    network = init_network()
    losses, gradient_norms = [], []
    for _ in range(steps):
        loss, gradients = backpropagate(network, features, labels)
        losses.append(loss)
        gradient_norms.append(float(np.linalg.norm(gradients.hidden_weights)))
        gradient_descent_step(network, gradients, learning_rate)
    return network, losses, gradient_norms


def show_learning() -> None:
    """Open a staged learning GUI, or complete one update without a window."""
    is_headless = os.environ.get("FORMACAO_ML_NO_PAUSE") == "1"
    interface = LearningInterface(*load_binary_demo_examples(), animate=not is_headless)
    try:
        if is_headless:
            for _ in range(10):
                interface.advance()
            step = interface.demo.step
            print(f"Rede 2-2-2, label {step.label}, uma atualização: perda {step.loss_before:.6f} -> {step.loss_after:.6f}.")
        else:
            plt.show()
    finally:
        interface.timer.stop()
        plt.close(interface.figure)


def main() -> None:
    show_learning()


if __name__ == "__main__":
    main()
