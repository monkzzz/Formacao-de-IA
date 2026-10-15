"""Interactive comparison of labels, discovered groups and reward-based learning."""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent
from matplotlib.widgets import Button
from numpy.typing import NDArray

from apoio.formato_pt import numero
from apoio.ajuste_janela import fit_window
from apoio.flappy_bird import FlappyBird, train_flappy_bird
from apoio.flappy_bird_ui import FlappyBirdInterface

FloatArray = NDArray[np.float64]
IndexArray = NDArray[np.int64]
SEED = 12
CLASS_COLORS = ("#00a8cc", "#ec9736")
GROUP_COLORS = ("#8863bc", "#548348", "#4285b4", "#b96c8c")


def make_labelled_sessions(seed: int = SEED) -> tuple[FloatArray, IndexArray]:
    """Return synthetic sessions (pages, exit rate) with a known purchase label."""
    random = np.random.default_rng(seed)
    buyers = random.normal((5.5, 0.25), (1.0, 0.07), size=(30, 2))
    browsers = random.normal((2.5, 0.65), (1.0, 0.07), size=(30, 2))
    return np.vstack((browsers, buyers)), np.repeat(np.array((0, 1), dtype=np.int64), 30)


def validate_features(features: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Validate the model boundary and return standardization parameters."""
    if features.ndim != 2 or len(features) < 2 or not np.isfinite(features).all():
        raise ValueError("Os atributos devem ser uma matriz finita com pelo menos duas sessões.")
    spread = features.std(axis=0)
    if features.shape[1] == 0 or np.any(spread == 0):
        raise ValueError("Cada atributo deve ter variação para poder ser normalizado.")
    return features.mean(axis=0), spread


def fit_logistic_regression(
    features: FloatArray, labels: IndexArray, steps: int = 400, learning_rate: float = 0.5,
) -> tuple[FloatArray, float]:
    """Fit a binary linear classifier on standardized features."""
    mean, spread = validate_features(features)
    if labels.shape != (len(features),) or not np.isin(labels, (0, 1)).all():
        raise ValueError("É necessário um label binário (0 ou 1) para cada sessão.")
    if steps < 1 or not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("Os passos e a taxa de aprendizagem devem ser positivos.")
    scaled = (features - mean) / spread
    weights = np.zeros(scaled.shape[1])
    bias = 0.0
    for _ in range(steps):
        probabilities = 1.0 / (1.0 + np.exp(-np.clip(scaled @ weights + bias, -500, 500)))
        error = probabilities - labels
        weights -= learning_rate * scaled.T @ error / len(labels)
        bias -= learning_rate * float(error.mean())
    # Fold standardization into raw-feature weights for new-session inference.
    raw_weights = weights / spread
    return raw_weights, float(bias - mean @ raw_weights)


def predict_purchase(features: FloatArray, weights: FloatArray, bias: float) -> IndexArray:
    """Predict purchase labels using fitted raw-feature parameters."""
    return (features @ weights + bias > 0).astype(np.int64)


def assign_groups(points: FloatArray, centers: FloatArray, spread: FloatArray) -> IndexArray:
    """Assign sessions to the nearest center using the training feature scales."""
    distances = (((points[:, None, :] - centers[None, :, :]) / spread) ** 2).sum(axis=2)
    return distances.argmin(axis=1).astype(np.int64)


def fit_kmeans(
    points: FloatArray, cluster_count: int, seed: int = SEED, iterations: int = 25,
) -> tuple[IndexArray, FloatArray]:
    """Discover groups without labels, using Lloyd's algorithm on scaled features."""
    mean, spread = validate_features(points)
    if not isinstance(cluster_count, int) or not 1 <= cluster_count <= len(points):
        raise ValueError("cluster_count deve estar entre 1 e o número de sessões.")
    if iterations < 1:
        raise ValueError("iterations deve ser positivo.")
    scaled = (points - mean) / spread
    random = np.random.default_rng(seed)
    centers = scaled[random.choice(len(scaled), cluster_count, replace=False)].copy()
    for _ in range(iterations):
        assignments = assign_groups(scaled, centers, np.ones(points.shape[1]))
        for group in range(cluster_count):
            members = scaled[assignments == group]
            if len(members):
                centers[group] = members.mean(axis=0)
    raw_centers = centers * spread + mean
    # Reassign against the final centers, including when iterations=1.
    return assign_groups(points, raw_centers, spread), raw_centers


class SessionLearningInterface:
    """Apply two models to the same new session selected by the presenter."""

    def __init__(self) -> None:
        self.sessions, self.labels = make_labelled_sessions()
        self.is_trained = False
        self.cluster_count = 2
        self.example_index = 0
        self.new_session: FloatArray | None = None
        self.weights = np.zeros(2)
        self.bias = 0.0
        self.groups = np.zeros(len(self.sessions), dtype=np.int64)
        self.centers = np.zeros((2, 2))
        self.figure, self.axes = plt.subplots(1, 2, figsize=(14, 8), facecolor="#f6fafb")
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Sessões e modelos")
        self.figure.subplots_adjust(left=0.075, right=0.97, bottom=0.36, top=0.77, wspace=0.20)
        self.figure.suptitle("Os mesmos dados · dois tipos de aprendizagem", fontsize=23, weight="bold", y=0.97)
        self.figure.text(0.075, 0.885, "Cada ponto é uma sessão de uma loja online. Mudamos a informação dada ao modelo.", fontsize=14)
        self.status = self.figure.text(0.075, 0.235, "", fontsize=14, color="#005b65")
        self.figure.text(0.075, 0.035, "Dados sintéticos · cores dos grupos não são respostas de compra · nova sessão não altera o treino", fontsize=11, color="#52666d")
        self._create_controls()
        self.figure.canvas.mpl_connect("button_press_event", self.select_session)
        self.render()

    def _create_controls(self) -> None:
        actions = (
            ("Treinar modelos", self.train), ("Nova sessão", self.next_example),
            ("Grupos: 2 → 3 → 4", self.change_groups), ("Reiniciar", self.reset),
            ("Flappy Bird →", self.finish),
        )
        self.buttons: list[Button] = []
        for index, (label, callback) in enumerate(actions):
            axis = self.figure.add_axes((0.075 + index * 0.18, 0.115, 0.16, 0.06))
            button = Button(axis, label, color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(11)
            button.on_clicked(callback)
            self.buttons.append(button)

    def train(self, event: MouseEvent | None = None) -> None:
        """Fit the classifier with labels and the clustering model without labels."""
        self.weights, self.bias = fit_logistic_regression(self.sessions, self.labels)
        self.groups, self.centers = fit_kmeans(self.sessions, self.cluster_count)
        self.is_trained = True
        self.render()

    def next_example(self, event: MouseEvent | None = None) -> None:
        """Select a prepared synthetic session for prediction in both views."""
        if not self.is_trained:
            self.status.set_text("Primeiro, clica em «Treinar modelos» para revelar a fronteira e os grupos.")
            self.figure.canvas.draw_idle()
            return
        examples = ((4.1, 0.40), (6.0, 0.30), (2.0, 0.65), (3.7, 0.50))
        self.new_session = np.array(examples[self.example_index % len(examples)])
        self.example_index += 1
        self.render()

    def select_session(self, event: MouseEvent) -> None:
        """Use a click in either chart as the same new input to both models."""
        if event.inaxes not in self.axes or event.button != 1:
            return
        if event.xdata is None or event.ydata is None:
            return
        if not self.is_trained:
            self.status.set_text("Clica em «Treinar modelos» antes de experimentar uma sessão.")
            self.figure.canvas.draw_idle()
            return
        self.new_session = np.array((event.xdata, event.ydata / 100))
        self.render()

    def change_groups(self, event: MouseEvent | None = None) -> None:
        """Change requested K without changing the classifier or using labels."""
        self.cluster_count = 2 + (self.cluster_count - 1) % 3
        if self.is_trained:
            self.groups, self.centers = fit_kmeans(self.sessions, self.cluster_count)
        self.render()

    def reset(self, event: MouseEvent | None = None) -> None:
        """Return to the original data-only view without regenerating the sample."""
        self.is_trained = False
        self.cluster_count = 2
        self.example_index = 0
        self.new_session = None
        self.render()

    def finish(self, event: MouseEvent | None = None) -> None:
        """Close this stage so the entry point proceeds to reinforcement learning."""
        plt.close(self.figure)

    def _configure_axis(self, axis: plt.Axes) -> None:
        axis.clear()
        axis.set(xlim=(0, 8.5), ylim=(0, 100))
        axis.set_xlabel("Páginas de produto visitadas", fontsize=13)
        axis.set_ylabel("Taxa de saída (%)", fontsize=13)
        axis.grid(alpha=0.15)
        axis.tick_params(labelsize=11)
        axis.set_facecolor("white")

    def _plot_supervised(self) -> None:
        axis = self.axes[0]
        self._configure_axis(axis)
        axis.set_title("Supervisionada · respostas conhecidas\nRegressão logística", fontsize=16, pad=15)
        if self.is_trained:
            pages, exits = np.meshgrid(np.linspace(0, 8.5, 80), np.linspace(0, 100, 80))
            scores = self.weights[0] * pages + self.weights[1] * exits / 100 + self.bias
            axis.contour(pages, exits, scores, levels=[0], colors=["#172b33"], linewidths=2)
        for label, name, color, marker in ((1, "Comprou", CLASS_COLORS[0], "o"), (0, "Não comprou", CLASS_COLORS[1], "s")):
            members = self.labels == label
            axis.scatter(self.sessions[members, 0], self.sessions[members, 1] * 100, s=65, color=color, marker=marker, label=name, edgecolor="white", linewidth=0.6)
        axis.legend(fontsize=11, loc="upper right")

    def _plot_unsupervised(self) -> None:
        axis = self.axes[1]
        self._configure_axis(axis)
        axis.set_title(f"Não supervisionada · sem respostas\nK-means · {self.cluster_count} grupos pedidos", fontsize=16, pad=15)
        if not self.is_trained:
            axis.scatter(self.sessions[:, 0], self.sessions[:, 1] * 100, s=65, color="#a8b6bc", edgecolor="white")
            return
        for group in range(self.cluster_count):
            members = self.groups == group
            axis.scatter(self.sessions[members, 0], self.sessions[members, 1] * 100, s=65, color=GROUP_COLORS[group], label=f"Grupo {group + 1}", edgecolor="white")
        axis.scatter(self.centers[:, 0], self.centers[:, 1] * 100, marker="X", s=180, color="#172b33", label="Centros", edgecolor="white")
        axis.legend(fontsize=11, loc="upper right")

    def _plot_new_session(self) -> None:
        if self.new_session is None:
            return
        point = self.new_session
        for axis in self.axes:
            # Above the legend (zorder 5): a click in the upper corner must still show the new session.
            axis.scatter(point[0], point[1] * 100, marker="*", s=300, color="#f4d341", edgecolor="#172b33", linewidth=1.5, zorder=10)
        prediction = int(predict_purchase(point[None, :], self.weights, self.bias)[0])
        group = int(assign_groups(point[None, :], self.centers, self.sessions.std(axis=0))[0])
        label = "comprou" if prediction else "não comprou"
        self.status.set_text(
            f"★ Nova sessão: {numero(point[0], '.1f')} páginas · saída {numero(point[1], '.0%')}\n"
            f"Supervisionada: prevê «{label}»    |    Não supervisionada: atribui ao Grupo {group + 1}"
        )

    def render(self) -> None:
        """Refresh the two views, keeping training data separate from inference."""
        self._plot_supervised()
        self._plot_unsupervised()
        message = "Clica em «Treinar modelos»: à esquerda usamos as respostas; à direita retiramos essas respostas."
        if self.is_trained:
            message = "A linha separa previsões de compra. Os X são centros dos grupos.\nClica num gráfico ou em «Nova sessão» para experimentar os dois modelos."
        self.status.set_text(message)
        if self.is_trained:
            self._plot_new_session()
        self.figure.canvas.draw_idle()


def show_paradigms() -> None:
    """Open the comparison directly, returning when the presenter closes it."""
    interface = SessionLearningInterface()
    try:
        if os.environ.get("FORMACAO_ML_NO_PAUSE") == "1":
            interface.train()
            interface.next_example()
        else:
            plt.show()
    finally:
        plt.close(interface.figure)


def show_flappy_bird_exercise() -> None:
    """Open the paused game or run a short noninteractive smoke demonstration."""
    is_headless = os.environ.get("FORMACAO_ML_NO_PAUSE") == "1"
    interface = FlappyBirdInterface(animate=not is_headless)
    try:
        if is_headless:
            for _ in range(100):
                interface.learner.advance()
            interface.render()
        else:
            plt.show()
    finally:
        plt.close(interface.figure)


def main() -> None:
    """Present sessions first, then an inspectable action/reward learning loop."""
    show_paradigms()
    show_flappy_bird_exercise()


if __name__ == "__main__":
    main()
