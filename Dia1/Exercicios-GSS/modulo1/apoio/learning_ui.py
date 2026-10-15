"""Presenter-controlled loss, backpropagation and repeated training on a tiny MLP."""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import CloseEvent, KeyEvent, MouseEvent
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.text import Text
from matplotlib.widgets import Button, Slider

from .ajuste_janela import fit_window
from .forward_pass_demo import CLASSES, FloatArray, LabelArray
from .learning_demo import LearningDemo, LearningStage as Stage, target_vector

TEAL, ORANGE, INK, MUTED = "#008694", "#c76d1b", "#172b33", "#52666d"
BACKGROUND = "#f6fafb"
INPUT_COLORS = ("#00a8cc", "#eb9836")
POSITIONS = {"x1": (1., 3.), "x2": (1., 1.), "h1": (6., 3.),
             "h2": (6., 1.), "o0": (11., 3.), "o5": (11., 1.)}
TITLES = ("A mesma rede do exercício 2", "Forward pass: calcular os scores",
          "Softmax e resposta conhecida", "Perda: medir a previsão",
          "Gradientes dos scores", "Gradientes dos pesos e bias da saída",
          "Propagar os gradientes à camada oculta", "Gradientes dos pesos e bias ocultos",
          "Otimização: atualizar todos os parâmetros", "Novo forward com a mesma imagem",
          "Comparar o resultado e continuar o treino")
PHASES = ("Forward pass", "Perda", "Backpropagation", "Otimização", "Repetir")
# Phase of the training cycle shown by each stage (softmax is the end of the forward pass).
STAGE_PHASE = {Stage.NETWORK: 0, Stage.FORWARD: 0, Stage.PROBABILITIES: 0, Stage.LOSS: 1,
               Stage.OUTPUT_DELTA: 2, Stage.OUTPUT_PARAMETERS: 2, Stage.HIDDEN_DELTA: 2,
               Stage.HIDDEN_PARAMETERS: 2, Stage.UPDATE: 3, Stage.NEW_FORWARD: 4, Stage.COMPARISON: 4}
TRAINING_PERIOD, CYCLE_PERIOD = 2, 20
# Moving dots reach the hidden layer at .4 and the outputs (or a weight) at .8 of the stage;
# the value they carry is written only when they arrive.
HIDDEN_ARRIVAL, OUTPUT_ARRIVAL = .4, .8
REST_COLOR = "#b8cbd1"


@dataclass(frozen=True)
class Flow:
    """A value travelling along the links of one layer: arrow and moving dot share this direction.

    Visual grammar of the whole animation: teal = values (forward), orange = gradients
    (backward); arrow + moving dot = something travels along a link; pulsing ring = a
    calculation done inside a node; grey link without arrow = at rest.
    """

    layer: str  # "hidden" = links x → H, "output" = links H → s
    is_gradient: bool
    reaches_weight: bool  # a weight gradient stops on its weight (δ × input); it is not propagated
    window: tuple[float, float]


FORWARD_FLOWS = (Flow("hidden", False, False, (0., HIDDEN_ARRIVAL)), Flow("output", False, False, (HIDDEN_ARRIVAL, OUTPUT_ARRIVAL)))
STAGE_FLOWS = {
    Stage.FORWARD: FORWARD_FLOWS,
    Stage.NEW_FORWARD: FORWARD_FLOWS,
    Stage.OUTPUT_PARAMETERS: (Flow("output", True, True, (0., OUTPUT_ARRIVAL)),),
    Stage.HIDDEN_DELTA: (Flow("output", True, False, (0., OUTPUT_ARRIVAL)),),
    Stage.HIDDEN_PARAMETERS: (Flow("hidden", True, True, (0., OUTPUT_ARRIVAL)),),
}


def number(value: float, decimals: int = 4) -> str:
    """Keep Portuguese separators without hiding the sign of a small gradient."""
    if value == 0:
        return "0"
    if value != 0 and abs(value) < 10 ** -decimals:
        return f"{value:.2e}".replace(".", ",")
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".").replace(".", ",")


class LearningInterface:
    """Inspect each computation, then optionally animate several complete SGD cycles."""

    def __init__(self, images: FloatArray, labels: LabelArray, animate: bool = True,
                 training_cycles: int = 20) -> None:
        if not isinstance(training_cycles, int) or training_cycles <= 0:
            raise ValueError("O número de ciclos de treino deve ser um inteiro positivo.")
        self.demo = LearningDemo(images, labels)
        self.training_cycles = training_cycles
        self.training_goal: int | None = None
        self.is_running, self.is_training, self.has_timer = False, False, animate
        self.frame, self.input_slot, self.focus = 0, 0, ("hidden", 0)
        self.flow_dots: list[Circle] = []
        self.flow_paths: list[tuple[tuple[float, float], tuple[float, float], float, float]] = []
        self.node_texts: dict[str, object] = {}
        self.pulses: list[tuple[object, bool]] = []  # (ring or link, is_link) that pulse while animating
        # (text, value, placeholder, arrival): a value is written only when its dot arrives.
        self.reveals: list[tuple[Text, str, str, float]] = []
        self.figure = plt.figure(figsize=(16, 9), facecolor=BACKGROUND)
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Perda, backpropagation e otimização")
        self.heading = self.figure.text(.045, .94, "", fontsize=23, weight="bold", color=INK)
        self.status = self.figure.text(.045, .884, "", fontsize=14, color=TEAL)
        self.phase_texts = [self.figure.text(.655 + index * .078, .888, phase, fontsize=11, ha="center",
                                             bbox={"boxstyle": "round,pad=.35", "edgecolor": "none"})
                            for index, phase in enumerate(PHASES)]
        self.image_axis = self.figure.add_axes((.045, .49, .21, .33))
        self.main_axis = self.figure.add_axes((.29, .43, .68, .40))
        self.detail_axis = self.figure.add_axes((.045, .205, .70, .20))
        self.summary_axis = self.figure.add_axes((.79, .22, .18, .17))
        self.footer = self.figure.text(.045, .015, "", fontsize=10, color=MUTED)
        self.rate_hint = self.figure.text(.38, .143, "", fontsize=11, color=MUTED)
        self._syncing_rate = False
        self.buttons: list[Button] = []
        self._create_controls()
        self.timer = self.figure.canvas.new_timer(interval=120)
        self.timer.add_callback(self.tick)
        self.figure.canvas.mpl_connect("button_press_event", self.select_item)
        self.figure.canvas.mpl_connect("key_press_event", self.on_key)
        self.figure.canvas.mpl_connect("close_event", self.close)
        self.render()

    def _create_controls(self) -> None:
        actions = (("← Anterior", self.previous), ("Próximo →", self.advance),
                   ("Animar ciclo", self.toggle_running), ("Treinar +20", self.toggle_training),
                   ("Nova iteração", self.next_iteration), ("Outro dígito", self.next_example),
                   ("Novos pesos", self.randomize), ("Reiniciar", self.reset))
        for index, (label, callback) in enumerate(actions):
            axis = self.figure.add_axes((.045 + index * .116, .065, .104, .050))
            button = Button(axis, label, color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(11)
            button.on_clicked(callback)
            self.buttons.append(button)
        axis = self.figure.add_axes((.105, .14, .24, .026))
        self.rate_slider = Slider(axis, "Taxa α", .01, 3., valinit=.1, valstep=.01, color=TEAL)
        self.rate_slider.on_changed(self.change_rate)
        axis = self.figure.add_axes((.045, .414, .21, .028))
        self.pixel_button = Button(axis, "Escolher entrada 1", color="#e1eff2", hovercolor="#c1e3e9")
        self.pixel_button.label.set_fontsize(10)
        self.pixel_button.on_clicked(self.change_slot)

    def _pause(self, clear_training: bool = False) -> None:
        self.is_running = False
        self.timer.stop()
        self.frame = 0
        if clear_training:
            self.is_training = False
            self.training_goal = None

    def _advance_stage(self) -> None:
        self.demo.advance()
        if self.demo.stage in (Stage.OUTPUT_DELTA, Stage.OUTPUT_PARAMETERS):
            self.focus = ("output", CLASSES.index(self.demo.label))
        elif self.demo.stage in (Stage.HIDDEN_DELTA, Stage.HIDDEN_PARAMETERS):
            self.focus = ("hidden", 0)

    def advance(self, event: MouseEvent | None = None) -> None:
        """Reveal one step; after the comparison, start the next cycle with the same image."""
        if self.demo.stage == Stage.COMPARISON:
            self.next_iteration()
            return
        self._pause(clear_training=True)
        self._advance_stage()
        self.render()

    def previous(self, event: MouseEvent | None = None) -> None:
        """Revisit a snapshot without undoing or duplicating an applied update."""
        self._pause(clear_training=True)
        self.demo.go_back()
        self._match_focus()
        self.render()

    def _match_focus(self) -> None:
        if self.demo.stage in (Stage.OUTPUT_DELTA, Stage.OUTPUT_PARAMETERS, Stage.PROBABILITIES):
            self.focus = ("output", CLASSES.index(self.demo.label))
        elif self.demo.stage in (Stage.HIDDEN_DELTA, Stage.HIDDEN_PARAMETERS):
            self.focus = ("hidden", 0)

    def next_iteration(self, event: MouseEvent | None = None) -> None:
        """Use the learned network for another step on the same visible sample."""
        self._pause(clear_training=True)
        try:
            self.demo.next_iteration()
        except ValueError as error:
            self._show_error(error)
            return
        self.focus = ("hidden", 0)
        self.render()

    def next_example(self, event: MouseEvent | None = None) -> None:
        """Keep the trained parameters and the fixed-set loss curve."""
        self._pause(clear_training=True)
        self.demo.next_example()
        self.focus = ("hidden", 0)
        self.render()

    def randomize(self, event: MouseEvent | None = None) -> None:
        """Begin another reproducible trial with new weights and biases."""
        self._pause(clear_training=True)
        self.demo.randomize()
        self.render()

    def reset(self, event: MouseEvent | None = None) -> None:
        """Restore the initial digit, pixels, parameters, learning rate and history."""
        self._pause(clear_training=True)
        self.demo.reset()
        self.focus, self.input_slot = ("hidden", 0), 0
        self._syncing_rate = True
        try:
            self.rate_slider.set_val(self.demo.learning_rate)
        finally:
            self._syncing_rate = False
        self.render()

    def change_rate(self, value: float) -> None:
        """Choose the rate before applying this cycle, without learning implicitly."""
        if self._syncing_rate:
            return
        self._pause(clear_training=True)
        try:
            self.demo.set_learning_rate(float(value))
        except ValueError as error:
            self._show_error(error)
            return
        self.render()

    def change_slot(self, event: MouseEvent | None = None) -> None:
        """Choose which input a subsequent image click will replace."""
        self.input_slot = 1 - self.input_slot
        self.render()

    def toggle_running(self, event: MouseEvent | None = None) -> None:
        """Animate only this cycle, stopping at the final comparison."""
        if self.is_running:
            self._pause(clear_training=True)
        elif self.demo.stage != Stage.COMPARISON:
            self.is_running, self.is_training, self.training_goal = True, False, None
            self.frame = 0
            if self.has_timer:
                self.timer.start()
        self.render()

    def toggle_training(self, event: MouseEvent | None = None) -> None:
        """Animate complete cycles through training digits, with pause/resume."""
        if self.is_running and self.is_training:
            self._pause()
        else:
            if self.training_goal is None:
                self.training_goal = self.demo.total_updates + self.training_cycles
            self.is_running, self.is_training, self.frame = True, True, 0
            if self.demo.stage == Stage.COMPARISON:
                self.demo.next_iteration(advance_example=True)
            if self.has_timer:
                self.timer.start()
        self.render()

    def tick(self) -> None:
        """Move values along links and repeat whole cycles only in training mode."""
        if not self.is_running:
            return
        self.frame += 1
        period = TRAINING_PERIOD if self.is_training else CYCLE_PERIOD
        if self.frame >= period:
            self.frame = 0
            self._play_next_stage()
            self.render()
        else:
            self._move_flow_dots(self.frame / period)
            self.figure.canvas.draw_idle()

    def _move_flow_dots(self, fraction: float) -> None:
        """Each dot travels only inside its time window, so layers run one after the other."""
        for dot, (start, end, begin, finish) in zip(self.flow_dots, self.flow_paths):
            local = min(1.0, max(0.0, (fraction - begin) / (finish - begin)))
            dot.set_visible(begin <= fraction <= finish)
            dot.center = tuple(a + local * (b - a) for a, b in zip(start, end))
        for text, value, placeholder, arrival in self.reveals:
            text.set_text(value if fraction >= arrival else placeholder)
        wave = .5 - .5 * np.cos(2 * np.pi * fraction * 2)  # two pulses per stage
        for artist, is_link in self.pulses:
            if is_link:
                artist.set_linewidth(2.5 + 2.5 * wave)
            else:
                artist.set_linewidth(2.5 + 2.5 * wave)
                artist.set_alpha(1 - .65 * wave)

    def _play_next_stage(self) -> None:
        if self.demo.stage != Stage.COMPARISON:
            self._advance_stage()
            if self.demo.stage == Stage.COMPARISON and not self.is_training:
                self._pause(clear_training=True)
            return
        assert self.training_goal is not None
        if self.demo.total_updates >= self.training_goal:
            self._pause(clear_training=True)
        else:
            self.demo.next_iteration(advance_example=True)
            self.focus = ("hidden", 0)

    def on_key(self, event: KeyEvent) -> None:
        """Use arrows, Space, T, N and R for the presenter controls."""
        playback = self.toggle_training if self.is_training else self.toggle_running
        callbacks = {"right": self.advance, "left": self.previous, " ": playback,
                     "t": self.toggle_training, "n": self.next_iteration, "r": self.reset}
        if event.key in callbacks:
            callbacks[event.key]()

    def close(self, event: CloseEvent) -> None:
        """Stop playback when the window closes."""
        self._pause(clear_training=True)

    def _show_error(self, error: ValueError) -> None:
        self.footer.set_text(str(error))
        self.figure.canvas.draw_idle()

    def select_item(self, event: MouseEvent) -> None:
        """Map image clicks to inputs, or inspect a relevant neuron during a step."""
        if event.button != 1 or event.xdata is None or event.ydata is None:
            return
        if event.inaxes == self.image_axis and self.demo.stage == Stage.NETWORK:
            col, row = int(np.floor(event.xdata + .5)), int(np.floor(event.ydata + .5))
            if 0 <= row < 8 and 0 <= col < 8:
                self._pause(clear_training=True)
                try:
                    self.demo.select_pixel(self.input_slot, row * 8 + col)
                except ValueError as error:
                    self._show_error(error)
                    return
                self.input_slot = 1 - self.input_slot
                self.render()
        elif event.inaxes == self.main_axis:
            self._select_neuron(event.xdata, event.ydata)

    def _select_neuron(self, x: float, y: float) -> None:
        for name, center in POSITIONS.items():
            if name.startswith("x") or np.hypot(x - center[0], y - center[1]) > .5:
                continue
            kind = "hidden" if name.startswith("h") else "output"
            stage = self.demo.stage
            if stage in (Stage.OUTPUT_DELTA, Stage.OUTPUT_PARAMETERS, Stage.PROBABILITIES) and kind != "output":
                return
            if stage in (Stage.HIDDEN_DELTA, Stage.HIDDEN_PARAMETERS) and kind != "hidden":
                return
            self._pause()
            index = int(name[1]) - 1 if kind == "hidden" else CLASSES.index(int(name[1]))
            self.focus = (kind, index)
            self.render()

    def _draw_image(self) -> None:
        axis = self.image_axis
        axis.clear()
        axis.imshow(self.demo.image, cmap="gray_r", vmin=0, vmax=16, interpolation="nearest")
        axis.set_title(f"Resposta conhecida: {self.demo.label}", fontsize=16, pad=12)
        axis.set_xticks([])
        axis.set_yticks([])
        for slot, index in enumerate(self.demo.pixel_indices):
            row, col = divmod(index, 8)
            axis.add_patch(Rectangle((col - .5, row - .5), 1, 1, fill=False, lw=3,
                                     edgecolor=INPUT_COLORS[slot]))
        for slot, value in enumerate(self.demo.inputs):
            axis.text(slot * .56, -.12, f"x{slot + 1} = {number(value)}", transform=axis.transAxes,
                      fontsize=12, color=INPUT_COLORS[slot], weight="bold")

    def _node_value(self, name: str) -> str:
        stage, step = self.demo.stage, self.demo.step
        result = step.forward_after if stage >= Stage.NEW_FORWARD else step.forward_before
        if name.startswith("x"):
            index = int(name[1]) - 1
            return f"x{index + 1}\n{number(self.demo.inputs[index])}"
        is_hidden = name.startswith("h")
        index = int(name[1]) - 1 if is_hidden else CLASSES.index(int(name[1]))
        if stage in (Stage.NETWORK, Stage.UPDATE):
            return f"H{index + 1}" if is_hidden else f"s{CLASSES[index]}"
        if is_hidden:
            if stage in (Stage.HIDDEN_DELTA, Stage.HIDDEN_PARAMETERS):
                return f"δH{index + 1}\n{number(step.gradients.hidden_deltas[index])}"
            return f"H{index + 1}\n{number(result.hidden_activations[index])}"
        if Stage.OUTPUT_DELTA <= stage <= Stage.HIDDEN_PARAMETERS:
            return f"δs{CLASSES[index]}\n{number(step.gradients.score_deltas[index])}"
        # The new forward pass shows scores like the first one; probabilities belong to softmax,
        # the loss and the final comparison.
        shows_probability = stage in (Stage.PROBABILITIES, Stage.LOSS, Stage.COMPARISON)
        value = result.probabilities[index] if shows_probability else result.scores[index]
        return (f"p{CLASSES[index]}" if shows_probability else f"s{CLASSES[index]}") + "\n" + number(value)

    def _flow(self, layer: str) -> Flow | None:
        """The value travelling along this layer's links at this stage, if any."""
        return next((flow for flow in STAGE_FLOWS.get(self.demo.stage, ()) if flow.layer == layer), None)

    def _pulsing_nodes(self) -> tuple[tuple[str, ...], bool]:
        """Nodes where this stage computes in place, and whether it is a gradient (orange)."""
        label_node = f"o{self.demo.label}"
        return {
            Stage.PROBABILITIES: (("o0", "o5"), False),
            Stage.LOSS: ((label_node,), True),
            Stage.OUTPUT_DELTA: (("o0", "o5"), True),
            Stage.UPDATE: (("h1", "h2", "o0", "o5"), True),
            Stage.COMPARISON: ((label_node,), False),
        }.get(self.demo.stage, ((), False))

    def _node_arrival(self, name: str) -> tuple[str, float] | None:
        """Placeholder and arrival time of a node value carried there by a moving dot."""
        stage, index = self.demo.stage, name[1]
        if stage in (Stage.FORWARD, Stage.NEW_FORWARD) and not name.startswith("x"):
            return (f"H{index}", HIDDEN_ARRIVAL) if name.startswith("h") else (f"s{index}", OUTPUT_ARRIVAL)
        if stage == Stage.HIDDEN_DELTA and name.startswith("h"):
            return f"δH{index}", OUTPUT_ARRIVAL
        return None

    def _edge_text(self, layer: str, j: int, i: int) -> str:
        step, stage = self.demo.step, self.demo.stage
        old = step.before.output_weights if layer == "output" else step.before.hidden_weights
        new = step.after.output_weights if layer == "output" else step.after.hidden_weights
        gradients = step.gradients.output_weights if layer == "output" else step.gradients.hidden_weights
        # Hidden deltas use the old output WEIGHTS as chain-rule factors.
        # Showing their gradients here would suggest multiplying the wrong values.
        reveal_gradient = stage in (Stage.OUTPUT_PARAMETERS, Stage.HIDDEN_PARAMETERS) if layer == "output" else stage == Stage.HIDDEN_PARAMETERS
        if reveal_gradient:
            return "g = " + number(gradients[j, i])
        if stage == Stage.UPDATE:
            return f"{number(old[j, i], 3)} → {number(new[j, i], 3)}"
        weights = new if stage >= Stage.NEW_FORWARD else old
        return "w = " + number(weights[j, i])

    def _draw_links(self, sources: tuple[str, str], targets: tuple[str, str], layer: str) -> None:
        flow, is_update = self._flow(layer), self.demo.stage == Stage.UPDATE
        for j, destination in enumerate(targets):
            for i, source in enumerate(sources):
                a, c = POSITIONS[source], POSITIONS[destination]
                fraction = .28 if i == j else .74
                weight_point = tuple(a[k] + fraction * (c[k] - a[k]) for k in range(2))
                # A neuron with ReLU′ = 0 receives no gradient: its incoming weights do not change.
                is_blocked = (flow is not None and flow.is_gradient and layer == "hidden"
                              and self.demo.step.gradients.hidden_deltas[j] == 0)
                link = FancyArrowPatch(a, c, arrowstyle="-", shrinkA=33, shrinkB=33,
                                       color=ORANGE if is_update else REST_COLOR, lw=2.5 if is_update else 1)
                self.main_axis.add_patch(link)
                if is_update:
                    self.pulses.append((link, True))
                if flow is not None and not is_blocked:
                    self._draw_flow(flow, a, c, weight_point)
                offset = .27 if i == j == 0 else (-.28 if i == j else (.1 if j == 0 else -.15))
                value = self._edge_text(layer, j, i)
                text = self.main_axis.text(weight_point[0], weight_point[1] + offset, value,
                    ha="center", fontsize=11, color=ORANGE if is_update or value.startswith("g") else INK,
                    bbox={"facecolor": BACKGROUND, "edgecolor": "none", "pad": 1})
                if self.is_running and flow is not None and flow.reaches_weight and not is_blocked:
                    self.reveals.append((text, text.get_text(), "g = …", flow.window[1]))

    def _draw_flow(self, flow: Flow, source: tuple[float, float], destination: tuple[float, float],
                   weight_point: tuple[float, float]) -> None:
        """Arrow (and, while animating, a moving dot) in the direction the value travels."""
        start, end = (destination, source) if flow.is_gradient else (source, destination)
        if flow.reaches_weight:
            end = weight_point
        color = ORANGE if flow.is_gradient else TEAL
        self.main_axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, shrinkA=33,
                                                 shrinkB=0 if flow.reaches_weight else 33, color=color, lw=2, zorder=2))
        if self.is_running:
            direction = (np.array(end) - np.array(start)) / np.linalg.norm(np.array(end) - np.array(start))
            first = tuple(np.array(start) + .55 * direction)
            last = tuple(np.array(end) - (0 if flow.reaches_weight else .55) * direction)
            dot = Circle(first, .10, color=color, zorder=5, visible=flow.window[0] == 0)
            self.main_axis.add_patch(dot)
            self.flow_dots.append(dot)
            self.flow_paths.append((first, last, *flow.window))

    def _bias_text(self, name: str) -> str:
        step, stage = self.demo.step, self.demo.stage
        is_hidden = name.startswith("h")
        index = int(name[1]) - 1 if is_hidden else CLASSES.index(int(name[1]))
        old = step.before.hidden_bias if is_hidden else step.before.output_bias
        new = step.after.hidden_bias if is_hidden else step.after.output_bias
        gradient = step.gradients.hidden_bias if is_hidden else step.gradients.output_bias
        if stage == Stage.UPDATE:
            return f"b: {number(old[index], 3)} → {number(new[index], 3)}"
        is_gradient = stage == Stage.HIDDEN_PARAMETERS if is_hidden else Stage.OUTPUT_PARAMETERS <= stage <= Stage.HIDDEN_PARAMETERS
        if is_gradient:
            return "g(b) = " + number(gradient[index])
        return "b = " + number((new if stage >= Stage.NEW_FORWARD else old)[index])

    def _draw_network(self) -> None:
        axis = self.main_axis
        axis.clear()
        axis.set(xlim=(0, 12), ylim=(-.1, 4.2), aspect="equal")
        axis.set_axis_off()
        self.flow_dots, self.flow_paths, self.pulses, self.reveals = [], [], [], []
        self._draw_links(("x1", "x2"), ("h1", "h2"), "hidden")
        self._draw_links(("h1", "h2"), ("o0", "o5"), "output")
        for x, label in ((1, "2 entradas"), (6, "2 neurónios · ReLU"), (11, "Classes 0 e 5")):
            axis.text(x, 3.92, label, ha="center", fontsize=14, color=TEAL, weight="bold")
        pulsing, is_gradient = self._pulsing_nodes()
        for name in pulsing:
            ring = Circle(POSITIONS[name], .58, fill=False, edgecolor=ORANGE if is_gradient else TEAL, lw=3, zorder=2)
            axis.add_patch(ring)
            self.pulses.append((ring, False))
        for name, center in POSITIONS.items():
            color = INPUT_COLORS[int(name[1]) - 1] if name.startswith("x") else TEAL
            kind = "hidden" if name.startswith("h") else "output"
            index = int(name[1]) - 1 if kind == "hidden" else CLASSES.index(int(name[1])) if name.startswith("o") else -1
            is_selected = not name.startswith("x") and self.focus == (kind, index)
            axis.add_patch(Circle(center, .48, facecolor=color, edgecolor=ORANGE if is_selected else "white", lw=3, zorder=3))
            self.node_texts[name] = axis.text(*center, self._node_value(name), ha="center", va="center",
                                              fontsize=11, color="white", weight="bold", zorder=4)
            arrival = self._node_arrival(name)
            if self.is_running and arrival is not None:
                self.reveals.append((self.node_texts[name], self._node_value(name), *arrival))
            if not name.startswith("x"):
                bias = self._bias_text(name)
                # Orange marks gradients and updates only, as on the weights.
                axis.text(center[0], center[1] - .84, bias, ha="center", fontsize=11,
                          color=INK if bias.startswith("b =") else ORANGE)
        if self.is_running:
            self._move_flow_dots(0.0)

    def _forward_lines(self) -> tuple[str, ...]:
        step = self.demo.step
        result = step.forward_after if self.demo.stage >= Stage.NEW_FORWARD else step.forward_before
        params = step.after if self.demo.stage >= Stage.NEW_FORWARD else step.before
        kind, index = self.focus
        is_hidden = kind == "hidden"
        weights = params.hidden_weights[index] if is_hidden else params.output_weights[index]
        bias = params.hidden_bias[index] if is_hidden else params.output_bias[index]
        values = result.inputs if is_hidden else result.hidden_activations
        total = result.hidden_sums[index] if is_hidden else result.scores[index]
        name = f"H{index + 1}" if is_hidden else f"Score da classe {CLASSES[index]}"
        equation = " + ".join(f"{number(v)} × ({number(w)})" for v, w in zip(values, weights))
        final = f"ReLU({number(total)}) = {number(result.hidden_activations[index])}" if is_hidden else f"Score = {number(total)}"
        return (name + " · clica noutro neurónio para ver as contas",
                equation + f" + ({number(bias)})", f"Soma = {number(total)}", final)

    def _output_delta_lines(self) -> tuple[str, ...]:
        result, gradients = self.demo.step.forward_before, self.demo.step.gradients
        expected = target_vector(self.demo.label)
        return ("Softmax + entropia cruzada: ∂L/∂s = p − y",
                f"Classe 0: {number(result.probabilities[0])} − {number(expected[0])} = {number(gradients.score_deltas[0])}",
                f"Classe 5: {number(result.probabilities[1])} − {number(expected[1])} = {number(gradients.score_deltas[1])}",
                "São gradientes dos scores. Ainda não alterámos os parâmetros.")

    def _hidden_delta_lines(self) -> tuple[str, ...]:
        step, index = self.demo.step, self.focus[1]
        g, weights = step.gradients, step.before.output_weights[:, index]
        unmasked = g.hidden_contributions[:, index].sum()
        equation = " + ".join(f"({number(w)}) × ({number(delta)})" for w, delta in zip(weights, g.score_deltas))
        return (f"H{index + 1}: somar os caminhos de regresso e aplicar a derivada da ReLU",
                equation + f" = {number(unmasked)}",
                f"zH{index + 1} = {number(step.forward_before.hidden_sums[index])}     ReLU′ = {number(g.relu_slopes[index])}",
                f"δH{index + 1} = {number(unmasked)} × {number(g.relu_slopes[index])} = {number(g.hidden_deltas[index])}")

    def _parameter_gradient_lines(self, is_hidden: bool) -> tuple[str, ...]:
        step, index = self.demo.step, self.focus[1]
        gradients = step.gradients
        delta = gradients.hidden_deltas[index] if is_hidden else gradients.score_deltas[index]
        inputs = step.forward_before.inputs if is_hidden else step.forward_before.hidden_activations
        weights = gradients.hidden_weights[index] if is_hidden else gradients.output_weights[index]
        name = f"H{index + 1}" if is_hidden else f"Score da classe {CLASSES[index]}"
        return (name + ": gradiente do peso = δ × entrada recebida",
                f"∂L/∂w₁ = {number(delta)} × {number(inputs[0])} = {number(weights[0])}",
                f"∂L/∂w₂ = {number(delta)} × {number(inputs[1])} = {number(weights[1])}",
                f"∂L/∂b = δ = {number(delta)}")

    def _update_lines(self) -> tuple[str, ...]:
        step = self.demo.step
        is_hidden, index = self.focus[0] == "hidden", self.focus[1]
        before = step.before.hidden_weights[index] if is_hidden else step.before.output_weights[index]
        after = step.after.hidden_weights[index] if is_hidden else step.after.output_weights[index]
        gradient = step.gradients.hidden_weights[index] if is_hidden else step.gradients.output_weights[index]
        old_bias = step.before.hidden_bias[index] if is_hidden else step.before.output_bias[index]
        new_bias = step.after.hidden_bias[index] if is_hidden else step.after.output_bias[index]
        bias_gradient = step.gradients.hidden_bias[index] if is_hidden else step.gradients.output_bias[index]
        rate = number(step.learning_rate)
        name = f"H{index + 1}" if is_hidden else f"Score da classe {CLASSES[index]}"
        return (f"{name}: novo = atual − α × gradiente. Atualizamos todos em simultâneo.",
                f"w₁: {number(before[0])} − {rate} × ({number(gradient[0])}) = {number(after[0])}",
                f"w₂: {number(before[1])} − {rate} × ({number(gradient[1])}) = {number(after[1])}",
                f"bias: {number(old_bias)} − {rate} × ({number(bias_gradient)}) = {number(new_bias)}")

    def _comparison_lines(self) -> tuple[str, ...]:
        step, index = self.demo.step, CLASSES.index(self.demo.label)
        old, new = step.forward_before.probabilities[index], step.forward_after.probabilities[index]
        before = CLASSES[int(step.forward_before.probabilities.argmax())]
        after = CLASSES[int(step.forward_after.probabilities.argmax())]
        mean_before, mean_after = self.demo.loss_history[-2:] if len(self.demo.loss_history) > 1 else (0., 0.)
        # The update used this image only: the other class can get worse, so the mean may rise.
        mean_note = "desceu" if mean_after < mean_before else "subiu: só usámos esta imagem; a outra classe piorou"
        return ("Mesma imagem e mesmos píxeis. Comparar antes e depois desta atualização.",
                f"p(classe {self.demo.label}): {number(old)} → {number(new)}     Previsão: {before} → {after}",
                f"Perda desta imagem: {number(step.loss_before)} → {number(step.loss_after)}",
                f"Média das {len(self.demo.source.images)} imagens: {number(mean_before)} → {number(mean_after)} "
                f"({mean_note}).")

    def _detail_lines(self) -> tuple[str, ...]:
        stage, step = self.demo.stage, self.demo.step
        if stage in (Stage.FORWARD, Stage.NEW_FORWARD):
            return self._forward_lines()
        if stage == Stage.OUTPUT_DELTA:
            return self._output_delta_lines()
        if stage == Stage.HIDDEN_DELTA:
            return self._hidden_delta_lines()
        if stage in (Stage.OUTPUT_PARAMETERS, Stage.HIDDEN_PARAMETERS):
            return self._parameter_gradient_lines(stage == Stage.HIDDEN_PARAMETERS)
        if stage == Stage.UPDATE:
            return self._update_lines()
        if stage == Stage.COMPARISON:
            return self._comparison_lines()
        if stage == Stage.PROBABILITIES:
            probabilities, scores = step.forward_before.probabilities, step.forward_before.scores
            return (f"Resposta conhecida: {self.demo.label}     Alvo one-hot: {target_vector(self.demo.label).astype(int).tolist()}",
                    f"Scores: s0 = {number(scores[0])}     s5 = {number(scores[1])}",
                    f"Softmax: p0 = {number(probabilities[0])}     p5 = {number(probabilities[1])}",
                    "A perda usará a probabilidade atribuída à resposta conhecida.")
        if stage == Stage.LOSS:
            correct = step.forward_before.probabilities[CLASSES.index(self.demo.label)]
            return (f"O label é {self.demo.label}. Medimos a probabilidade dessa classe.",
                    f"L = −ln(p{self.demo.label})", f"p{self.demo.label} = {number(correct)}     L = {number(step.loss_before)}",
                    f"Aqui, a perda desta imagem. À direita, a média das {len(self.demo.source.images)} imagens de treino.")
        first = ("As mesmas duas entradas do exercício 2, agora com aprendizagem." if not self.demo.total_updates
                 else f"Novo ciclo com os parâmetros já atualizados (atualizações: {self.demo.total_updates}).")
        return (first,
                f"x1 = {number(self.demo.inputs[0])}     x2 = {number(self.demo.inputs[1])}     Resposta conhecida = {self.demo.label}",
                f"Taxa de aprendizagem α = {number(self.demo.learning_rate)}",
                "Avança para calcular a previsão. Clica na imagem para escolher os píxeis.")

    def _draw_detail(self) -> None:
        axis = self.detail_axis
        axis.clear()
        axis.set_axis_off()
        for index, line in enumerate(self._detail_lines()):
            axis.text(0, .93 - index * .27, line, fontsize=15 if index in (0, 3) else 19,
                      color=TEAL if index == 0 else INK, weight="bold" if index == 0 else "normal")

    def _draw_summary(self) -> None:
        axis = self.summary_axis
        axis.clear()
        if self.demo.stage == Stage.PROBABILITIES:
            axis.bar(np.arange(2) - .18, self.demo.step.forward_before.probabilities, .36,
                     color=TEAL, label="Previsto")
            axis.bar(np.arange(2) + .18, target_vector(self.demo.label), .36,
                     color=ORANGE, alpha=.65, label="Alvo")
            axis.set(ylim=(0, 1.18), xticks=(0, 1), xticklabels=CLASSES)
            axis.set_title("Previsão e resposta", fontsize=12)
            axis.legend(fontsize=9, loc="upper right")
        elif self.demo.stage >= Stage.LOSS or self.demo.total_updates:
            self._draw_loss_history()
        else:
            axis.set_axis_off()
            axis.text(.05, .5, "Depois da perda,\nacompanhamos o treino.", fontsize=13, color=MUTED)
        axis.tick_params(labelsize=9)

    def _draw_loss_history(self) -> None:
        # Hide this cycle's new loss until the final comparison, even after
        # rewinding. The applied model itself is never undone by presentation.
        count = len(self.demo.loss_history) - int(self.demo.is_applied and self.demo.stage < Stage.COMPARISON)
        count = max(1, count)
        values, steps = self.demo.loss_history[:count], self.demo.history_updates[:count]
        axis = self.summary_axis
        axis.plot(steps, values, color=TEAL, marker="o", markersize=4, lw=1.8)
        axis.set_title(f"Perda média nos {len(self.demo.source.images)}\nexemplos de treino", fontsize=12)
        axis.set_xlabel("Atualizações aplicadas", fontsize=10)
        axis.grid(alpha=.2)
        axis.set_xticks(np.unique(np.linspace(steps[0], steps[-1], min(4, len(steps))).astype(int)))
        if len(steps) == 1:
            axis.set_xlim(max(0, steps[0] - .5), steps[0] + 1)

    def _update_controls(self) -> None:
        self.buttons[2].label.set_text("Pausar" if self.is_running and not self.is_training else "Animar ciclo")
        train_label = "Pausar treino" if self.is_training and self.is_running else "Retomar treino" if self.training_goal is not None else f"Treinar +{self.training_cycles}"
        self.buttons[3].label.set_text(train_label)
        can_continue = self.demo.stage == Stage.COMPARISON
        self.buttons[4].set_active(can_continue)
        self.buttons[4].ax.set_facecolor("#e1eff2" if can_continue else "#edf0f1")
        self.rate_slider.set_active(not self.demo.is_applied)
        self.rate_slider.valtext.set_text(number(self.demo.learning_rate))
        self.rate_hint.set_text("Taxa fixada nesta atualização. Nova iteração permite alterá-la."
                               if self.demo.is_applied else "Ajusta α antes da atualização. A alteração não treina a rede.")
        self.pixel_button.label.set_text(f"Escolher entrada {self.input_slot + 1}")
        self.pixel_button.ax.set_visible(self.demo.stage == Stage.NETWORK)
        self.pixel_button.set_active(self.demo.stage == Stage.NETWORK)

    def _draw_phases(self) -> None:
        current = STAGE_PHASE[self.demo.stage]
        for index, text in enumerate(self.phase_texts):
            is_current = index == current
            text.set_color("white" if is_current else MUTED)
            text.set_fontweight("bold" if is_current else "normal")
            text.get_bbox_patch().set_facecolor(ORANGE if is_current and index in (1, 2, 3) else
                                                TEAL if is_current else "#e1eff2")

    def render(self) -> None:
        """Reveal only the values for this stage and keep training progress explicit."""
        stage = self.demo.stage
        title = "Parâmetros de entrada deste ciclo" if stage == Stage.NETWORK and self.demo.total_updates else TITLES[int(stage)]
        self.heading.set_text(f"{int(stage) + 1}/11   {title}")
        status = f"Amostra {self.demo.source.example_index + 1}/{len(self.demo.source.images)}   ·   label: {self.demo.label}   ·   α = {number(self.demo.learning_rate)}   ·   atualizações: {self.demo.total_updates}"
        if self.training_goal is not None:
            status += f"   ·   treino {'em curso' if self.is_running else 'pausado'}: faltam {max(0, self.training_goal - self.demo.total_updates)}"
        self.status.set_text(status)
        self._draw_phases()
        self._draw_image()
        self._draw_network()
        self._draw_detail()
        self._draw_summary()
        self._update_controls()
        self.footer.set_text("2 dos 64 píxeis · classes 0/5 · um exemplo por atualização · curva no conjunto de treino da demo · teste reservado · ecrã arredondado")
        self.figure.canvas.draw_idle()
