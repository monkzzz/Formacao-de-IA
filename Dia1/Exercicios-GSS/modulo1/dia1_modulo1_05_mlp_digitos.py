"""Train and inspect a small PyTorch MLP on the UCI handwritten digits."""

from __future__ import annotations

import os
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.backend_bases import MouseEvent
from matplotlib.container import BarContainer
from matplotlib.image import AxesImage
from matplotlib.text import Text
from matplotlib.widgets import Button
from numpy.typing import NDArray
from torch import nn
from torch.utils.data import TensorDataset

from apoio.digit_dataset import load_digit_splits

FloatArray = NDArray[np.float64]
IndexArray = NDArray[np.int64]
SEED = 23
HIDDEN_UNITS = 32
EPOCHS = 12
BATCH_SIZE = 128
LEARNING_RATE = 0.1
DRAWING_SIZE = 24
BRUSH_RADIUS = 1.5


@dataclass(frozen=True)
class EpochMetrics:
    """Training and validation measurements for one epoch."""

    train_loss: float
    validation_loss: float
    train_accuracy: float
    validation_accuracy: float


class DigitMLP(nn.Module):
    """A one-hidden-layer dense network with ten output scores."""

    def __init__(self, hidden_units: int = HIDDEN_UNITS) -> None:
        super().__init__()
        self.hidden_layer = nn.Linear(64, hidden_units)
        self.activation = nn.ReLU()
        self.output_layer = nn.Linear(hidden_units, 10)

    def forward_with_hidden(
        self,
        features: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Return hidden activations and raw class scores for inspection."""
        hidden_activations = self.activation(self.hidden_layer(features))
        return hidden_activations, self.output_layer(hidden_activations)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """Return raw class scores; CrossEntropyLoss consumes these logits."""
        _, scores = self.forward_with_hidden(features)
        return scores


def stratified_train_validation_split(
    labels: IndexArray,
    validation_fraction: float = 0.15,
    seed: int = SEED,
) -> tuple[IndexArray, IndexArray]:
    """Split official training indices per digit while preserving class coverage."""
    if labels.ndim != 1 or labels.size == 0:
        raise ValueError("As labels devem formar um vetor nao vazio.")
    if np.any((labels < 0) | (labels >= 10)):
        raise ValueError("As labels devem estar no intervalo 0-9.")
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction tem de estar entre 0 e 1.")
    random = np.random.default_rng(seed)
    train_parts = []
    validation_parts = []

    for digit in range(10):
        digit_indices = random.permutation(np.flatnonzero(labels == digit))
        if digit_indices.size < 2:
            raise ValueError(
                f"Sao necessarias pelo menos duas amostras de treino do digito {digit}."
            )
        validation_count = max(1, int(round(digit_indices.size * validation_fraction)))
        validation_count = min(validation_count, digit_indices.size - 1)
        validation_parts.append(digit_indices[:validation_count])
        train_parts.append(digit_indices[validation_count:])

    return (
        random.permutation(np.concatenate(train_parts)).astype(np.int64),
        random.permutation(np.concatenate(validation_parts)).astype(np.int64),
    )


def to_feature_tensor(images: FloatArray) -> torch.Tensor:
    """Flatten 8x8 pixels to 64 normalized floating-point inputs."""
    return torch.tensor(images.reshape(-1, 64) / 16.0, dtype=torch.float32)


def to_label_tensor(labels: IndexArray) -> torch.Tensor:
    """Convert digit labels to the integer class indices PyTorch expects."""
    return torch.tensor(labels, dtype=torch.long)


def draw_segment(
    drawing: FloatArray,
    start: tuple[float, float],
    end: tuple[float, float],
    brush_radius: float = BRUSH_RADIUS,
) -> None:
    """Paint an interpolated dark-ink segment into a 24x24 drawing canvas."""
    if drawing.shape != (DRAWING_SIZE, DRAWING_SIZE):
        raise ValueError(f"O desenho deve ter forma ({DRAWING_SIZE}, {DRAWING_SIZE}).")
    if brush_radius <= 0:
        raise ValueError("O raio do pincel deve ser positivo.")

    start_x, start_y = start
    end_x, end_y = end
    point_count = max(
        1,
        int(np.ceil(max(abs(end_x - start_x), abs(end_y - start_y)) * 2)),
    )
    for fraction in np.linspace(0.0, 1.0, point_count + 1):
        x = start_x + fraction * (end_x - start_x)
        y = start_y + fraction * (end_y - start_y)
        left = max(0, int(np.floor(x - brush_radius)))
        right = min(DRAWING_SIZE, int(np.ceil(x + brush_radius + 1)))
        top = max(0, int(np.floor(y - brush_radius)))
        bottom = min(DRAWING_SIZE, int(np.ceil(y + brush_radius + 1)))
        rows, columns = np.ogrid[top:bottom, left:right]
        inside_brush = (columns - x) ** 2 + (rows - y) ** 2 <= brush_radius**2
        drawing[top:bottom, left:right][inside_brush] = 16.0


def downsample_drawing(drawing: FloatArray) -> FloatArray:
    """Average a 24x24 mouse drawing into the dataset's normalized 8x8 pixels."""
    if drawing.shape != (DRAWING_SIZE, DRAWING_SIZE):
        raise ValueError(f"O desenho deve ter forma ({DRAWING_SIZE}, {DRAWING_SIZE}).")
    if np.any((drawing < 0.0) | (drawing > 16.0)):
        raise ValueError("As intensidades do desenho devem estar entre 0 e 16.")
    return drawing.reshape(8, 3, 8, 3).mean(axis=(1, 3))


def predict_drawn_digit(
    model: DigitMLP,
    drawing: FloatArray,
) -> tuple[int, FloatArray]:
    """Run inference on an 8x8 drawing and return its class and probabilities."""
    if drawing.shape != (8, 8):
        raise ValueError("A imagem desenhada deve ter forma (8, 8).")
    model.eval()
    with torch.no_grad():
        features = to_feature_tensor(drawing[np.newaxis, ...])
        probabilities = torch.softmax(model(features)[0], dim=0).numpy()
    return int(probabilities.argmax()), probabilities


class DigitDrawingInterface:
    """Matplotlib mouse canvas that runs inference with a trained digit model."""

    figure: plt.Figure
    drawing_axis: plt.Axes
    probabilities_axis: plt.Axes
    canvas_image: AxesImage
    bars: BarContainer
    status: Text
    infer_button: Button
    clear_button: Button

    def __init__(self, model: DigitMLP) -> None:
        self.model = model
        self.drawing = np.zeros((DRAWING_SIZE, DRAWING_SIZE), dtype=np.float64)
        self.last_point: tuple[int, int] | None = None
        self._build_figure()
        self._connect_events()

    def _build_figure(self) -> None:
        self.figure = plt.figure(figsize=(11, 6))
        grid = self.figure.add_gridspec(1, 2, width_ratios=(1, 1.3))
        self.drawing_axis = self.figure.add_subplot(grid[0, 0])
        self.probabilities_axis = self.figure.add_subplot(grid[0, 1])
        self.canvas_image = self.drawing_axis.imshow(
            self.drawing,
            cmap="gray_r",
            vmin=0,
            vmax=16,
            extent=(0, DRAWING_SIZE, DRAWING_SIZE, 0),
            interpolation="nearest",
        )
        self.drawing_axis.set(
            title="Desenha um digito (0-9)",
            xlim=(0, DRAWING_SIZE),
            ylim=(DRAWING_SIZE, 0),
            xticks=range(0, DRAWING_SIZE + 1, 3),
            yticks=range(0, DRAWING_SIZE + 1, 3),
        )
        self.drawing_axis.grid(color="#78a8bd", linewidth=0.5, alpha=0.6)
        self.probabilities_axis.set(
            title="Probabilidades previstas",
            xlabel="Digito",
            ylabel="Probabilidade",
            xticks=range(10),
            ylim=(0, 1),
        )
        self.bars = self.probabilities_axis.bar(
            range(10), np.zeros(10), color="#167d8d"
        )
        self.probabilities_axis.grid(axis="y", alpha=0.2)
        self.status = self.figure.text(
            0.5,
            0.12,
            "Desenha com o botao esquerdo; depois seleciona «Inferir».",
            ha="center",
        )
        self.figure.suptitle(
            "Inferencia exploratoria: o desenho nao altera nem avalia o modelo",
            fontsize=14,
        )
        self.figure.subplots_adjust(bottom=0.24, top=0.84, wspace=0.3)
        self.infer_button = Button(
            self.figure.add_axes((0.62, 0.04, 0.14, 0.07)),
            "Inferir",
        )
        self.clear_button = Button(
            self.figure.add_axes((0.78, 0.04, 0.14, 0.07)),
            "Limpar",
        )

    def _connect_events(self) -> None:
        canvas = self.figure.canvas
        canvas.mpl_connect("button_press_event", self._on_press)
        canvas.mpl_connect("motion_notify_event", self._on_motion)
        canvas.mpl_connect("button_release_event", self._on_release)
        self.infer_button.on_clicked(self._infer)
        self.clear_button.on_clicked(self._clear)

    def _get_canvas_point(self, event: MouseEvent) -> tuple[int, int] | None:
        if (
            event.inaxes is not self.drawing_axis
            or event.xdata is None
            or event.ydata is None
        ):
            return None
        column = int(np.clip(np.floor(event.xdata), 0, DRAWING_SIZE - 1))
        row = int(np.clip(np.floor(event.ydata), 0, DRAWING_SIZE - 1))
        return column, row

    def _on_press(self, event: MouseEvent) -> None:
        if event.button == 1:
            self.last_point = self._get_canvas_point(event)
            if self.last_point is not None:
                self._paint_to(self.last_point)

    def _on_motion(self, event: MouseEvent) -> None:
        if self.last_point is None or event.button != 1:
            return
        point = self._get_canvas_point(event)
        if point is None:
            return
        self._paint_to(point)

    def _on_release(self, _event: MouseEvent) -> None:
        self.last_point = None

    def _paint_to(self, point: tuple[int, int]) -> None:
        if self.last_point is not None:
            draw_segment(self.drawing, self.last_point, point)
        self.last_point = point
        self.canvas_image.set_data(self.drawing)
        self.status.set_text("Desenho pronto; seleciona «Inferir».")
        self.figure.canvas.draw_idle()

    def _infer(self, _event: MouseEvent) -> None:
        if not np.any(self.drawing):
            self.status.set_text("Desenha um digito antes de pedir a inferencia.")
            self.figure.canvas.draw_idle()
            return
        digit, probabilities = predict_drawn_digit(
            self.model,
            downsample_drawing(self.drawing),
        )
        for bar, probability in zip(self.bars, probabilities):
            bar.set_height(float(probability))
        self.probabilities_axis.set_title(
            f"Previsao: {digit} ({probabilities[digit]:.1%})"
        )
        self.status.set_text(
            "Inferencia apenas: escrita livre pode diferir dos digitos UCI "
            "e nao e uma metrica de avaliacao."
        )
        self.figure.canvas.draw_idle()

    def _clear(self, _event: MouseEvent) -> None:
        self.drawing.fill(0.0)
        self.canvas_image.set_data(self.drawing)
        for bar in self.bars:
            bar.set_height(0.0)
        self.probabilities_axis.set_title("Probabilidades previstas")
        self.status.set_text("Desenha com o botao esquerdo; depois seleciona «Inferir».")
        self.figure.canvas.draw_idle()

    def show(self) -> None:
        """Display the interactive canvas until the user closes it."""
        plt.show()


def show_drawing_inference(model: DigitMLP) -> None:
    """Let the user draw a digit and inspect the trained model's prediction."""
    if os.environ.get("FORMACAO_ML_NO_PAUSE") == "1":
        print("Inferencia por desenho omitida no modo automatizado.")
        return
    DigitDrawingInterface(model).show()


def summarize_classification(
    expected: IndexArray,
    predicted: IndexArray,
    class_count: int = 10,
) -> tuple[NDArray[np.int64], float, float, float, float]:
    """Return the confusion matrix, accuracy, and macro precision/recall/F1."""
    if expected.ndim != 1 or predicted.shape != expected.shape or expected.size == 0:
        raise ValueError("As labels esperadas e previstas devem ser vetores nao vazios iguais.")
    if class_count < 2 or np.any((expected < 0) | (expected >= class_count)):
        raise ValueError("As labels esperadas devem estar no intervalo das classes.")
    if np.any((predicted < 0) | (predicted >= class_count)):
        raise ValueError("As labels previstas devem estar no intervalo das classes.")

    confusion = np.zeros((class_count, class_count), dtype=np.int64)
    np.add.at(confusion, (expected, predicted), 1)
    true_positives = confusion.diagonal().astype(np.float64)
    precision = np.divide(
        true_positives,
        confusion.sum(axis=0),
        out=np.zeros(class_count),
        where=confusion.sum(axis=0) != 0,
    )
    recall = np.divide(
        true_positives,
        confusion.sum(axis=1),
        out=np.zeros(class_count),
        where=confusion.sum(axis=1) != 0,
    )
    f1 = np.divide(
        2 * precision * recall,
        precision + recall,
        out=np.zeros(class_count),
        where=(precision + recall) != 0,
    )
    return (
        confusion,
        float(true_positives.sum() / expected.size),
        float(precision.mean()),
        float(recall.mean()),
        float(f1.mean()),
    )


def measure(
    model: DigitMLP,
    features: torch.Tensor,
    labels: torch.Tensor,
    loss_function: nn.CrossEntropyLoss,
) -> tuple[float, float]:
    """Measure mean cross-entropy and accuracy without updating parameters."""
    model.eval()
    with torch.no_grad():
        scores = model(features)
        loss = float(loss_function(scores, labels).item())
        accuracy = float((scores.argmax(dim=1) == labels).float().mean().item())
    return loss, accuracy


def train_model(
    train_features: torch.Tensor,
    train_labels: torch.Tensor,
    validation_features: torch.Tensor,
    validation_labels: torch.Tensor,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    seed: int = SEED,
) -> tuple[DigitMLP, list[EpochMetrics]]:
    """Train the MLP and record train/validation metrics for every epoch."""
    if epochs < 1 or batch_size < 1 or learning_rate <= 0:
        raise ValueError("epochs, batch_size e learning_rate devem ser positivos.")
    if train_features.ndim != 2 or train_features.shape[1] != 64:
        raise ValueError("As features de treino devem ter forma (amostras, 64).")
    if validation_features.ndim != 2 or validation_features.shape[1] != 64:
        raise ValueError("As features de validacao devem ter forma (amostras, 64).")
    if train_features.shape[0] == 0 or validation_features.shape[0] == 0:
        raise ValueError("Treino e validacao devem conter amostras.")
    if train_features.shape[0] != train_labels.shape[0]:
        raise ValueError("As features e labels de treino devem ter o mesmo tamanho.")
    if validation_features.shape[0] != validation_labels.shape[0]:
        raise ValueError("As features e labels de validacao devem ter o mesmo tamanho.")

    torch.manual_seed(seed)
    random = torch.Generator().manual_seed(seed)
    model = DigitMLP()
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    metrics = []
    dataset = TensorDataset(train_features, train_labels)

    for _ in range(epochs):
        model.train()
        for batch_features, batch_labels in torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            generator=random,
        ):
            optimizer.zero_grad()
            scores = model(batch_features)
            loss = loss_function(scores, batch_labels)
            loss.backward()
            optimizer.step()

        train_loss, train_accuracy = measure(
            model, train_features, train_labels, loss_function
        )
        validation_loss, validation_accuracy = measure(
            model, validation_features, validation_labels, loss_function
        )
        metrics.append(
            EpochMetrics(
                train_loss,
                validation_loss,
                train_accuracy,
                validation_accuracy,
            )
        )

    return model, metrics


def main() -> None:
    """Walk through training, final evaluation and drawing in one GUI."""
    import sys
    from apoio.digit_training_demo import DigitTrainingDemo
    from apoio.digit_training_ui import DigitTrainingInterface

    torch.set_num_threads(1)
    demo = DigitTrainingDemo(sys.modules[__name__])
    interface = DigitTrainingInterface(demo)
    if os.environ.get("FORMACAO_ML_NO_PAUSE") == "1":
        for _ in range(7):
            interface.advance()
        for _ in range(EPOCHS):
            demo.train_epoch()
        interface.evaluate()
        print("Final test:", demo.test_result[1:])
        plt.close(interface.figure)
    else:
        plt.show()


if __name__ == "__main__":
    main()
