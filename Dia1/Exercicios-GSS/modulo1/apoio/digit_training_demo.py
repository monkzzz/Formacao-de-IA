"""Incremental digit training with a validation checkpoint and final test freeze."""
from __future__ import annotations
from copy import deepcopy
from types import ModuleType
import numpy as np
import torch
from torch import nn


class DigitTrainingDemo:
    """Own the training state; use the exercise module's existing numerical API.

    The module boundary keeps the public functions in 05 compatible with the
    earlier lesson and tests. No test measurements occur during initialization
    or training. Re-evaluation reads the cached final result.
    """

    def __init__(self, api: ModuleType) -> None:
        self.api = api
        self.images, self.labels, self.test_images, self.test_labels = api.load_digit_splits()
        self.train_indices, self.validation_indices = api.stratified_train_validation_split(self.labels)
        self.train_features = api.to_feature_tensor(self.images[self.train_indices])
        self.train_labels = api.to_label_tensor(self.labels[self.train_indices])
        self.validation_features = api.to_feature_tensor(self.images[self.validation_indices])
        self.validation_labels = api.to_label_tensor(self.labels[self.validation_indices])
        self.reset()

    def reset(self) -> None:
        """Start a new deterministic demonstration, clearing the in-memory result."""
        torch.manual_seed(self.api.SEED)
        self.random = torch.Generator().manual_seed(self.api.SEED)
        self.model = self.api.DigitMLP()
        self.initial_model = deepcopy(self.model)
        self.loss_function = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=self.api.LEARNING_RATE)
        self.history = [self._measure_epoch()]
        self.best_loss = self.history[0].validation_loss
        self.best_epoch = self.epoch = self.updates = self.phase = self.cursor = 0
        self.best_state = deepcopy(self.model.state_dict())
        self.order = torch.randperm(len(self.train_features), generator=self.random)
        self.validation_example = 0
        self.is_frozen = False
        self.test_result = None
        self.final_model: nn.Module | None = None
        self.batch_indices: torch.Tensor | None = None
        self.batch_scores: torch.Tensor | None = None
        self.batch_loss: torch.Tensor | None = None
        self.last_loss = self.gradient_norm = self.weight_change = 0.0
        self.weight_before = self.model.hidden_layer.weight.detach().clone()
        self.last_gradient = torch.zeros_like(self.weight_before)
        self.last_delta = torch.zeros_like(self.weight_before)
        self.sample_probabilities = np.zeros(10)
        self.sample_after = np.zeros(10)
        self.sample_hidden = np.zeros(32)
        self.sample_label = 0
        self.sample_losses = np.zeros(0)
        # (position in epochs, batch loss) for every applied update, so each cycle shows on the curve.
        self.batch_history: list[tuple[float, float]] = []

    def _measure_epoch(self):
        train_loss, train_accuracy = self.api.measure(
            self.model, self.train_features, self.train_labels, self.loss_function)
        val_loss, val_accuracy = self.api.measure(
            self.model, self.validation_features, self.validation_labels, self.loss_function)
        return self.api.EpochMetrics(train_loss, val_loss, train_accuracy, val_accuracy)

    def advance_phase(self) -> int:
        """Do forward, loss, backward or one simultaneous SGD update exactly once."""
        if self.is_frozen:
            raise RuntimeError("O modelo está fixado para avaliação e inferência. Reinicia para uma nova demonstração.")
        if self.phase == 0:
            self._forward_batch()
        elif self.phase == 1:
            labels = self.train_labels[self.batch_indices]
            self.batch_loss = self.loss_function(self.batch_scores, labels)
            self.last_loss = float(self.batch_loss.item())
            self.sample_losses = nn.functional.cross_entropy(
                self.batch_scores.detach(), labels, reduction="none").numpy().copy()
        elif self.phase == 2:
            self.batch_loss.backward()
            self.last_gradient = self.model.hidden_layer.weight.grad.detach().clone()
            self.gradient_norm = float(self.last_gradient.norm())
        else:
            self._update_batch()
        completed = self.phase
        self.phase = (self.phase + 1) % 4
        return completed

    def _forward_batch(self) -> None:
        self.model.train()
        self.batch_indices = self.order[self.cursor:self.cursor + self.api.BATCH_SIZE]
        self.optimizer.zero_grad()
        self.weight_before = self.model.hidden_layer.weight.detach().clone()
        hidden, self.batch_scores = self.model.forward_with_hidden(self.train_features[self.batch_indices])
        self.sample_hidden = hidden[0].detach().numpy().copy()
        self.sample_probabilities = torch.softmax(self.batch_scores[0].detach(), dim=0).numpy().copy()
        self.sample_label = int(self.train_labels[self.batch_indices[0]])

    def _update_batch(self) -> None:
        self.optimizer.step()
        self.last_delta = self.model.hidden_layer.weight.detach() - self.weight_before
        self.weight_change = float(self.last_delta.norm())
        with torch.no_grad():
            _, scores = self.model.forward_with_hidden(self.train_features[self.batch_indices[:1]])
        self.sample_after = torch.softmax(scores[0], dim=0).numpy().copy()
        self.cursor += len(self.batch_indices)
        self.updates += 1
        self.batch_history.append((self.epoch + self.cursor / len(self.train_features), self.last_loss))
        if self.cursor == len(self.train_features):
            self._finish_epoch()
        # Keep only detached values after the update; no obsolete autograd graph.
        self.batch_scores = self.batch_scores.detach()
        self.batch_loss = self.batch_loss.detach()

    def _finish_epoch(self) -> None:
        self.epoch += 1
        metrics = self._measure_epoch()
        self.history.append(metrics)
        if metrics.validation_loss < self.best_loss:
            self.best_loss, self.best_epoch = metrics.validation_loss, self.epoch
            self.best_state = deepcopy(self.model.state_dict())
        self.cursor = 0
        self.order = torch.randperm(len(self.train_features), generator=self.random)

    def train_epoch(self) -> None:
        """Complete the current epoch, respecting a partly executed batch."""
        target = self.epoch + 1
        while self.epoch < target:
            self.advance_phase()

    @property
    def validation_image(self) -> np.ndarray:
        """The current inspection example always comes from validation."""
        return self.images[self.validation_indices[self.validation_example]]

    @property
    def validation_digit(self) -> int:
        """Known label of the validation inspection image."""
        return int(self.labels[self.validation_indices[self.validation_example]])

    def next_validation_example(self) -> None:
        """Inspect another validation image, without changing any parameters."""
        self.validation_example = (self.validation_example + 1) % len(self.validation_indices)

    def inspect(self, image: np.ndarray, initial: bool = False) -> tuple[np.ndarray, np.ndarray]:
        """Return ReLU activations and softmax without updating the model."""
        model = self.initial_model if initial else (self.final_model if self.is_frozen else self.model)
        model.eval()
        with torch.no_grad():
            hidden, scores = model.forward_with_hidden(self.api.to_feature_tensor(image[np.newaxis]))
        return hidden[0].numpy().copy(), torch.softmax(scores[0], dim=0).numpy().copy()

    def evaluate_test(self):
        """Freeze the validation-selected checkpoint and measure reserved test once."""
        if self.test_result is not None:
            return self.test_result
        if self.epoch < 1:
            raise RuntimeError("Conclui pelo menos uma época («Treinar +12») antes da avaliação final.")
        if self.phase != 0 or self.cursor != 0:
            raise RuntimeError(f"A época {self.epoch + 1} está a meio. Conclui-a com «Treinar +12» "
                               "antes da avaliação final.")
        final_model = deepcopy(self.model)
        final_model.load_state_dict(self.best_state)
        final_model.eval()
        with torch.no_grad():
            scores = final_model(self.api.to_feature_tensor(self.test_images))
            predicted = scores.argmax(dim=1).numpy().copy()
            loss = float(self.loss_function(scores, self.api.to_label_tensor(self.test_labels)))
        summary = self.api.summarize_classification(self.test_labels, predicted)
        self.final_model = final_model
        self.test_predictions = predicted
        self.test_predictions.setflags(write=False)
        self.test_result = (*summary, loss)
        self.test_result[0].setflags(write=False)
        self.is_frozen = True
        return self.test_result
