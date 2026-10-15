"""Exact calculations and reversible presentation of one 2–2–2 learning step."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import math

import numpy as np

from .forward_pass_demo import (
    CLASSES, SEED, DemoParameters, DemoResult, FloatArray, ForwardDemo,
    LabelArray, flatten_image, initialize_parameters, run_forward,
)

DEFAULT_RATE = .1


class LearningStage(IntEnum):
    """Reveal derivatives before applying the single update for this iteration."""

    NETWORK = 0
    FORWARD = 1
    PROBABILITIES = 2
    LOSS = 3
    OUTPUT_DELTA = 4
    OUTPUT_PARAMETERS = 5
    HIDDEN_DELTA = 6
    HIDDEN_PARAMETERS = 7
    UPDATE = 8
    NEW_FORWARD = 9
    COMPARISON = 10


@dataclass(frozen=True)
class LearningGradients:
    """Parameter gradients plus the intermediate chain-rule factors."""

    score_deltas: FloatArray
    hidden_contributions: FloatArray
    relu_slopes: FloatArray
    hidden_deltas: FloatArray
    hidden_weights: FloatArray
    hidden_bias: FloatArray
    output_weights: FloatArray
    output_bias: FloatArray


@dataclass(frozen=True)
class LearningStep:
    """Read-only before/after snapshots, all derived from the same old parameters."""

    label: int
    learning_rate: float
    before: DemoParameters
    forward_before: DemoResult
    loss_before: float
    gradients: LearningGradients
    after: DemoParameters
    forward_after: DemoResult
    loss_after: float


def parameter_arrays(parameters: DemoParameters) -> tuple[FloatArray, ...]:
    """Return parameters in a fixed order, shared by updates and verification."""
    return (parameters.hidden_weights, parameters.hidden_bias,
            parameters.output_weights, parameters.output_bias)


def immutable(values: FloatArray) -> FloatArray:
    """Own a read-only copy so snapshots cannot be changed through another alias."""
    result = np.array(values, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


def copy_parameters(parameters: DemoParameters) -> DemoParameters:
    """Detach a snapshot from the caller's mutable arrays."""
    return DemoParameters(*(immutable(array) for array in parameter_arrays(parameters)))


def snapshot_result(result: DemoResult) -> DemoResult:
    """Keep every forward value read-only when revisiting an earlier stage."""
    values = (result.inputs, result.hidden_contributions, result.hidden_sums,
              result.hidden_activations, result.output_contributions,
              result.scores, result.probabilities)
    return DemoResult(*(immutable(array) for array in values))


def target_vector(label: int) -> FloatArray:
    """Represent the known answer in class order (0, 5)."""
    if label not in CLASSES:
        raise ValueError("O label deve ser 0 ou 5.")
    target = np.zeros(2, dtype=np.float64)
    target[CLASSES.index(label)] = 1
    return immutable(target)


def cross_entropy_scores(scores: FloatArray, label: int) -> float:
    """Compute -log(p_correct) stably even if the displayed probability underflows."""
    if scores.shape != (2,) or not np.isfinite(scores).all():
        raise ValueError("São necessários dois scores finitos.")
    target_vector(label)
    shifted = scores - scores.max()
    return float(np.log(np.exp(shifted).sum()) - shifted[CLASSES.index(label)])


def calculate_gradients(result: DemoResult, parameters: DemoParameters, label: int) -> LearningGradients:
    """Apply softmax+cross-entropy and the ReLU chain rule to one sample."""
    score_deltas = result.probabilities - target_vector(label)
    contributions = parameters.output_weights * score_deltas[:, None]
    # We choose ReLU'(0)=0, matching the convention used in this course.
    slopes = (result.hidden_sums > 0).astype(np.float64)
    hidden_deltas = contributions.sum(axis=0) * slopes
    arrays = (score_deltas, contributions, slopes, hidden_deltas,
              np.outer(hidden_deltas, result.inputs), hidden_deltas,
              np.outer(score_deltas, result.hidden_activations), score_deltas)
    return LearningGradients(*(immutable(array) for array in arrays))


def update_parameters(parameters: DemoParameters, gradients: LearningGradients,
                      learning_rate: float) -> DemoParameters:
    """Return one simultaneous SGD update; never mutate the old parameters."""
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("A taxa de aprendizagem deve ser positiva e finita.")
    gradient_arrays = (gradients.hidden_weights, gradients.hidden_bias,
                       gradients.output_weights, gradients.output_bias)
    updated = []
    for parameter, gradient in zip(parameter_arrays(parameters), gradient_arrays):
        if gradient.shape != parameter.shape or not np.isfinite(gradient).all():
            raise ValueError("Gradiente incompatível com a forma do parâmetro ou não finito.")
        with np.errstate(over="ignore", invalid="ignore"):
            values = parameter - learning_rate * gradient
        if not np.isfinite(values).all():
            raise ValueError("A atualização produziu valores não finitos; reduz a taxa de aprendizagem.")
        updated.append(immutable(values))
    return DemoParameters(*updated)


def calculate_step(inputs: FloatArray, parameters: DemoParameters, label: int,
                   learning_rate: float = DEFAULT_RATE) -> LearningStep:
    """Derive a complete inspection snapshot without applying it to any model."""
    before = copy_parameters(parameters)
    result = snapshot_result(run_forward(inputs, before))
    if not np.isfinite(result.scores).all():
        raise ValueError("O forward pass produziu scores não finitos.")
    gradients = calculate_gradients(result, before, label)
    after = update_parameters(before, gradients, learning_rate)
    new_result = snapshot_result(run_forward(inputs, after))
    return LearningStep(label, learning_rate, before, result,
                        cross_entropy_scores(result.scores, label), gradients, after,
                        new_result, cross_entropy_scores(new_result.scores, label))


class LearningDemo:
    """Allow inspection and rewind while committing at most one update per cycle."""

    def __init__(self, images: FloatArray, labels: LabelArray) -> None:
        self.source = ForwardDemo(images, labels)
        self.reset()

    @property
    def image(self) -> FloatArray:
        """Return the same raw digit image used by the forward-pass exercise."""
        return self.source.image

    @property
    def inputs(self) -> FloatArray:
        """Read the two selected normalized intensities in the same order."""
        return self.source.inputs

    @property
    def label(self) -> int:
        """Return the known training answer, never a predicted class."""
        return int(self.source.labels[self.source.example_index])

    @property
    def pixel_indices(self) -> tuple[int, int]:
        """Expose the two row-major indices for the image highlighting."""
        return self.source.pixel_indices

    def _prepare_iteration(self) -> None:
        self.step = calculate_step(self.inputs, self.parameters, self.label, self.learning_rate)
        self.stage = LearningStage.NETWORK
        self.is_applied = False

    def mean_training_loss(self, parameters: DemoParameters) -> float:
        """Monitor a fixed set, so curves remain comparable across different digits."""
        losses = []
        for image, label in zip(self.source.images, self.source.labels):
            inputs = flatten_image(image)[list(self.pixel_indices)]
            result = run_forward(inputs, parameters)
            losses.append(cross_entropy_scores(result.scores, int(label)))
        return float(np.mean(losses))

    def _reset_history(self) -> None:
        self._prepare_iteration()
        self.loss_history = [self.mean_training_loss(self.parameters)]
        self.history_updates = [self.total_updates]

    def reset(self) -> None:
        """Restore the image, selected pixels, seed and learning rate of the first run."""
        self.source.reset()
        self.seed = SEED
        self.learning_rate = DEFAULT_RATE
        self.parameters = initialize_parameters(self.seed)
        self.total_updates = 0
        self._reset_history()

    def advance(self) -> None:
        """Reveal one stage; apply exactly once on reaching UPDATE."""
        next_stage = LearningStage(min(int(LearningStage.COMPARISON), int(self.stage) + 1))
        if next_stage == LearningStage.UPDATE and not self.is_applied:
            # Evaluate the complete monitoring set before committing. A failed
            # evaluation must leave parameters, counters and history consistent.
            mean_loss = self.mean_training_loss(self.step.after)
            self.parameters = self.step.after
            self.is_applied = True
            self.total_updates += 1
            self.loss_history.append(mean_loss)
            self.history_updates.append(self.total_updates)
        self.stage = next_stage

    def go_back(self) -> None:
        """Revisit the stored before/after calculations without changing the model."""
        self.stage = LearningStage(max(0, int(self.stage) - 1))

    def next_iteration(self, advance_example: bool = False) -> None:
        """Continue this sample or cycle through training examples with learned weights."""
        if self.stage != LearningStage.COMPARISON or not self.is_applied:
            raise ValueError("Conclui a comparação antes de iniciar uma nova iteração.")
        if advance_example:
            self.source.next_example()
        self._prepare_iteration()

    def set_learning_rate(self, value: float) -> None:
        """Change the proposed step only while this cycle has not been applied."""
        if self.is_applied:
            raise ValueError("A taxa desta atualização está fixada. Inicia uma nova iteração.")
        candidate = calculate_step(self.inputs, self.parameters, self.label, value)
        self.learning_rate, self.step = float(value), candidate

    def select_pixel(self, slot: int, index: int) -> None:
        """Change one input, retaining the current model and starting a new sample view."""
        self.source.select_pixel(slot, index)
        # Changing pixels changes the objective; restart its curve rather than
        # joining losses computed from different representations.
        self._reset_history()

    def next_example(self) -> None:
        """Change the digit while monitoring the same fixed training examples."""
        self.source.next_example()
        self._prepare_iteration()

    def randomize(self) -> None:
        """Reset training with a new reproducible random initialization."""
        self.seed += 1
        self.parameters = initialize_parameters(self.seed)
        self.total_updates = 0
        self._reset_history()
