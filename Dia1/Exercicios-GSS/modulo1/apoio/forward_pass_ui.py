"""A presenter-controlled, visual forward pass through a small untrained network."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import CloseEvent, KeyEvent, MouseEvent
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.widgets import Button

from .ajuste_janela import fit_window
from .forward_pass_demo import CLASSES, ForwardDemo, Stage, FloatArray, LabelArray

TEAL = "#008694"
ORANGE = "#c76d1b"
INK = "#172b33"
MUTED = "#52666d"
INPUT_COLORS = ("#00a8cc", "#eb9836")
TITLES = ("O dígito", "A matriz de intensidades", "Flatten: matriz para vetor",
          "Escolher duas entradas", "Inicializar pesos e bias", "Calcular o neurónio H1",
          "Calcular o neurónio H2", "Calcular os scores das classes",
          "Softmax: scores para probabilidades", "O resultado da primeira passagem")
POSITIONS = {"x1": (1.0, 3.0), "x2": (1.0, 1.0), "h1": (6.0, 3.0),
             "h2": (6.0, 1.0), "o0": (11.0, 3.0), "o5": (11.0, 1.0)}


def number(value: float, decimals: int = 4) -> str:
    """Keep pixel fractions exact to four decimals and use Portuguese separators."""
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".").replace(".", ",")


class ForwardPassInterface:
    """Walk from the same digit to its flattened pixels, network and output."""

    def __init__(self, images: FloatArray, labels: LabelArray, animate: bool = True) -> None:
        self.demo = ForwardDemo(images, labels)
        self.is_running = False
        self.frame = 0
        self.input_slot = 0
        self.focus = ("hidden", 0)
        self.flow_dots: list[Circle] = []
        self.flow_paths: list[tuple[tuple[float, float], tuple[float, float]]] = []
        self.figure = plt.figure(figsize=(16, 9), facecolor="#f6fafb")
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Forward pass")
        self.heading = self.figure.text(.045, .94, "", fontsize=24, weight="bold", color=INK)
        self.status = self.figure.text(.045, .883, "", fontsize=14, color=TEAL)
        self.image_axis = self.figure.add_axes((.045, .43, .23, .39))
        self.main_axis = self.figure.add_axes((.32, .39, .65, .44))
        self.detail_axis = self.figure.add_axes((.045, .17, .92, .19))
        self.footer = self.figure.text(.045, .025, "", fontsize=11, color=MUTED)
        self.buttons: list[Button] = []
        self._create_controls()
        self.timer = self.figure.canvas.new_timer(interval=120)
        self.timer.add_callback(self.tick)
        self.has_timer = animate
        self.figure.canvas.mpl_connect("button_press_event", self.select_item)
        self.figure.canvas.mpl_connect("key_press_event", self.on_key)
        self.figure.canvas.mpl_connect("close_event", self.close)
        self.render()

    def _create_controls(self) -> None:
        actions = (("← Anterior", self.previous), ("Próximo →", self.advance),
                   ("Animar", self.toggle_running), ("Novos parâmetros", self.randomize),
                   ("Outro dígito", self.next_example), ("Reiniciar", self.reset))
        for i, (label, callback) in enumerate(actions):
            axis = self.figure.add_axes((.045 + i * .155, .075, .14, .055))
            button = Button(axis, label, color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(12)
            button.on_clicked(callback)
            self.buttons.append(button)
        axis = self.figure.add_axes((.045, .367, .23, .046))
        self.pixel_button = Button(axis, "Escolher entrada 1", color="#e1eff2", hovercolor="#c1e3e9")
        self.pixel_button.on_clicked(self.change_slot)
        self.pixel_button.label.set_fontsize(11)

    def _pause(self) -> None:
        self.is_running = False
        self.timer.stop()
        self.frame = 0

    def advance(self, event: MouseEvent | None = None) -> None:
        """Pause playback and reveal one new step without modifying parameters."""
        self._pause()
        self._advance_stage()
        self.render()

    def _advance_stage(self) -> None:
        self.demo.advance()
        if self.demo.stage in (Stage.HIDDEN_ONE, Stage.HIDDEN_TWO):
            self.focus = ("hidden", int(self.demo.stage) - int(Stage.HIDDEN_ONE))
        elif self.demo.stage == Stage.SCORES:
            self.focus = ("output", 0)

    def previous(self, event: MouseEvent | None = None) -> None:
        """Revisit a stage while keeping the same random initialization."""
        self._pause()
        self.demo.go_back()
        if self.demo.stage <= Stage.HIDDEN_TWO:
            self.focus = ("hidden", 1 if self.demo.stage == Stage.HIDDEN_TWO else 0)
        self.render()

    def randomize(self, event: MouseEvent | None = None) -> None:
        """Show fresh random parameters, with the forward pass still to be done."""
        self._pause()
        self.demo.randomize()
        self.focus = ("hidden", 0)
        self.render()

    def next_example(self, event: MouseEvent | None = None) -> None:
        """Change the digit, conserving the initialized network for comparison."""
        self._pause()
        self.demo.next_example()
        self.render()

    def reset(self, event: MouseEvent | None = None) -> None:
        """Restore the original image, pixels, seed and uninitialized view."""
        self._pause()
        self.demo.reset()
        self.input_slot = 0
        self.focus = ("hidden", 0)
        self.render()

    def change_slot(self, event: MouseEvent | None = None) -> None:
        """Select which network input the next matrix/vector click will replace."""
        self.input_slot = 1 - self.input_slot
        self.render()

    def toggle_running(self, event: MouseEvent | None = None) -> None:
        """Pause or animate the same pass, including the row-by-row flatten."""
        if self.is_running:
            self._pause()
        elif self.demo.stage != Stage.RESULT:
            self.is_running = True
            self.frame = 0
            if self.has_timer:
                self.timer.start()
        self.render()

    def tick(self) -> None:
        """Move values along active links and advance every 2.4 seconds."""
        if not self.is_running:
            return
        self.frame += 1
        if self.frame >= 20:
            self.frame = 0
            self._advance_stage()
            if self.demo.stage == Stage.RESULT:
                self._pause()
            self.render()
        elif self.demo.stage == Stage.FLATTEN:
            self._draw_flatten()
            self.figure.canvas.draw_idle()
        else:
            for dot, (start, end) in zip(self.flow_dots, self.flow_paths):
                fraction = self.frame / 20
                dot.center = tuple(a + fraction * (b - a) for a, b in zip(start, end))
            self.figure.canvas.draw_idle()

    def on_key(self, event: KeyEvent) -> None:
        """Use arrows for discussion, Space for playback and R for restart."""
        callbacks = {"right": self.advance, "left": self.previous,
                     " ": self.toggle_running, "r": self.reset}
        if event.key in callbacks:
            callbacks[event.key]()

    def close(self, event: CloseEvent) -> None:
        """Stop the GUI timer when its window closes."""
        self._pause()

    def select_item(self, event: MouseEvent) -> None:
        """Map a pixel to the same flatten index, or inspect one visible neuron."""
        if event.button != 1 or event.xdata is None or event.ydata is None:
            return
        if self.demo.stage in (Stage.FLATTEN, Stage.INPUTS):
            index = self._clicked_pixel(event)
            if index is not None:
                self._select_pixel(index)
        elif event.inaxes == self.main_axis and self.demo.stage >= Stage.PARAMETERS:
            self._select_neuron(event.xdata, event.ydata)

    def _clicked_pixel(self, event: MouseEvent) -> int | None:
        if event.inaxes == self.image_axis:
            col, row = int(np.floor(event.xdata + .5)), int(np.floor(event.ydata + .5))
            return row * 8 + col if 0 <= row < 8 and 0 <= col < 8 else None
        if event.inaxes == self.main_axis and 1.2 <= event.ydata <= 1.8:
            index = int(np.floor(event.xdata + .5))
            return index if 0 <= index < 64 else None
        return None

    def _select_pixel(self, index: int) -> None:
        self._pause()
        try:
            self.demo.select_pixel(self.input_slot, index)
        except ValueError as error:
            self.footer.set_text(str(error))
            self.figure.canvas.draw_idle()
            return
        self.input_slot = 1 - self.input_slot
        self.render()

    def _select_neuron(self, x: float, y: float) -> None:
        for name, center in POSITIONS.items():
            if name.startswith("x") or np.hypot(x - center[0], y - center[1]) > .48:
                continue
            kind = "hidden" if name.startswith("h") else "output"
            index = int(name[1]) - 1 if kind == "hidden" else CLASSES.index(int(name[1]))
            if self.demo.stage != Stage.PARAMETERS and kind == "hidden" and self.demo.stage < Stage.HIDDEN_ONE + index:
                return
            if kind == "output" and self.demo.stage != Stage.PARAMETERS and self.demo.stage < Stage.SCORES:
                return
            self._pause()
            self.focus = (kind, index)
            self.render()

    def _draw_image(self) -> None:
        axis = self.image_axis
        axis.clear()
        axis.imshow(self.demo.image, cmap="gray_r", vmin=0, vmax=16, interpolation="nearest")
        axis.set_title(f"Dígito real: {self.demo.labels[self.demo.example_index]}", fontsize=17, pad=12)
        axis.set_xticks([])
        axis.set_yticks([])
        if self.demo.stage >= Stage.MATRIX:
            self._matrix_grid(axis, show_numbers=self.demo.stage >= Stage.FLATTEN)
        if self.demo.stage >= Stage.FLATTEN:
            for slot, index in enumerate(self.demo.pixel_indices):
                row, col = divmod(index, 8)
                axis.add_patch(Rectangle((col - .5, row - .5), 1, 1, fill=False,
                                         edgecolor=INPUT_COLORS[slot], lw=3))

    def _matrix_grid(self, axis: plt.Axes, show_numbers: bool) -> None:
        axis.set_xticks(np.arange(-.5, 8, 1), minor=True)
        axis.set_yticks(np.arange(-.5, 8, 1), minor=True)
        axis.grid(which="minor", color="#bbc7cb", lw=.5)
        axis.tick_params(which="minor", bottom=False, left=False)
        if show_numbers:
            for row, values in enumerate(self.demo.image):
                for col, value in enumerate(values):
                    axis.text(col, row, number(value), ha="center", va="center", fontsize=12,
                              color="white" if value >= 9 else INK)

    def _draw_data_stage(self) -> None:
        axis = self.main_axis
        axis.clear()
        axis.set_axis_off()
        if self.demo.stage == Stage.IMAGE:
            axis.text(.05, .68, "Uma imagem\n64 intensidades", fontsize=31, weight="bold", color=TEAL)
            axis.text(.05, .35, "O mesmo dígito será representado\npor números, linha a linha.", fontsize=19, linespacing=1.6)
        elif self.demo.stage == Stage.MATRIX:
            axis.set_axis_on()
            axis.imshow(self.demo.image, cmap="gray_r", vmin=0, vmax=16, interpolation="nearest")
            axis.set_xticks([])
            axis.set_yticks([])
            self._matrix_grid(axis, show_numbers=True)
            axis.set_title("8 linhas × 8 colunas   ·   0: claro   ·   16: escuro", fontsize=17)
        else:
            self._draw_flatten()

    def _draw_flatten(self) -> None:
        axis = self.main_axis
        axis.clear()
        axis.set(xlim=(-1, 64), ylim=(0, 3.8))
        axis.set_axis_off()
        values = self.demo.image.reshape(1, 64).copy()
        if self.is_running and self.demo.stage == Stage.FLATTEN:
            count = min(64, (self.frame // 2 + 1) * 8)
            values[:, count:] = np.nan
        colors = plt.get_cmap("gray_r").with_extremes(bad="#e1eff2")
        axis.imshow(values, extent=(-.5, 63.5, 1.2, 1.8), aspect="auto", cmap=colors, vmin=0, vmax=16)
        axis.text(0, 3.15, "Uma linha com os mesmos 64 valores", fontsize=23, weight="bold", color=TEAL)
        axis.text(0, 2.45, "Linha 1, depois linha 2, até à linha 8", fontsize=17)
        for index in range(0, 64, 8):
            axis.text(index, .99, str(index + 1), fontsize=11, ha="center", color=MUTED)
            axis.axvline(index - .5, ymin=1.2 / 3.8, ymax=1.8 / 3.8, color="#aabdc3", lw=.8)
        for slot, index in enumerate(self.demo.pixel_indices):
            axis.add_patch(Rectangle((index - .5, 1.2), 1, .6, fill=False, edgecolor=INPUT_COLORS[slot], lw=3))
            raw = self.demo.image.reshape(64)[index]
            value = f"Píxel {index + 1}: {number(raw)}"
            if self.demo.stage == Stage.INPUTS:
                value += f" / 16 = {number(raw / 16)}"
            axis.text(slot * 33, .38, value, fontsize=17, color=INPUT_COLORS[slot], weight="bold")

    def _node_value(self, name: str) -> str:
        result, stage = self.demo.result, self.demo.stage
        if name.startswith("x"):
            index = int(name[1]) - 1
            return f"x{index + 1}\n{number(self.demo.inputs[index])}"
        if name.startswith("h"):
            index = int(name[1]) - 1
            value = number(result.hidden_activations[index]) if result is not None and stage >= Stage.HIDDEN_ONE + index else "?"
            return f"H{index + 1}\n{value}"
        index = CLASSES.index(int(name[1]))
        value = number(result.scores[index]) if result is not None and stage >= Stage.SCORES else "?"
        return value

    def _active_target(self) -> str | None:
        if self.demo.stage in (Stage.HIDDEN_ONE, Stage.HIDDEN_TWO):
            return "h" + str(int(self.demo.stage) - int(Stage.HIDDEN_ONE) + 1)
        if self.demo.stage == Stage.SCORES:
            return "o" + str(CLASSES[self.focus[1]])
        return None

    def _draw_layer_links(self, source: tuple[str, str], target: tuple[str, str], weights: FloatArray) -> None:
        active = self._active_target()
        for j, destination in enumerate(target):
            for i, start in enumerate(source):
                a, b = POSITIONS[start], POSITIONS[destination]
                is_active = destination == active
                color = TEAL if weights[j, i] >= 0 else ORANGE
                self.main_axis.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=15,
                    shrinkA=34, shrinkB=34, color=color, lw=2.8 if is_active else 1.2, alpha=1 if is_active else .45))
                fraction = .30 if i == j else .73
                x, y = (a[k] + fraction * (b[k] - a[k]) for k in range(2))
                offset = .25 if i == j == 0 else (-.28 if i == j else (.10 if j == 0 else -.13))
                self.main_axis.text(x, y + offset, f"w = {number(weights[j, i])}", ha="center", fontsize=12,
                                    color=color, bbox={"facecolor": "#f6fafb", "edgecolor": "none", "pad": 1})
                if is_active and self.is_running:
                    delta = np.array(b) - np.array(a)
                    direction = delta / np.linalg.norm(delta)
                    start_point = tuple(np.array(a) + .55 * direction)
                    end_point = tuple(np.array(b) - .55 * direction)
                    dot = Circle(start_point, .10, color="#eb9836", zorder=5)
                    self.main_axis.add_patch(dot)
                    self.flow_dots.append(dot)
                    self.flow_paths.append((start_point, end_point))

    def _draw_network(self) -> None:
        axis = self.main_axis
        axis.clear()
        axis.set(xlim=(0, 12), ylim=(-.1, 4.25), aspect="equal")
        axis.set_axis_off()
        self.flow_dots, self.flow_paths = [], []
        parameters = self.demo.parameters
        assert parameters is not None
        self._draw_layer_links(("x1", "x2"), ("h1", "h2"), parameters.hidden_weights)
        self._draw_layer_links(("h1", "h2"), ("o0", "o5"), parameters.output_weights)
        for x, label in ((1, "2 entradas"), (6, "2 neurónios · ReLU"), (11, "2 scores")):
            axis.text(x, 3.92, label, ha="center", fontsize=15, color=TEAL, weight="bold")
        for name, center in POSITIONS.items():
            color = INPUT_COLORS[int(name[1]) - 1] if name.startswith("x") else TEAL
            axis.add_patch(Circle(center, .47, facecolor=color, edgecolor="white", lw=2, zorder=3))
            axis.text(*center, self._node_value(name), ha="center", va="center", fontsize=12 if name.startswith("o") else 13,
                      color="white", weight="bold", zorder=4)
            if name.startswith("o"):
                axis.text(center[0], center[1] + .60, "Classe " + name[1], ha="center", fontsize=12, color=INK)
            if not name.startswith("x"):
                index = int(name[1]) - 1 if name.startswith("h") else CLASSES.index(int(name[1]))
                bias = parameters.hidden_bias[index] if name.startswith("h") else parameters.output_bias[index]
                axis.text(center[0], center[1] - .70, "bias = " + number(bias), ha="center", fontsize=12, color=ORANGE)

    def _draw_neuron_detail(self) -> None:
        axis = self.detail_axis
        params, result = self.demo.parameters, self.demo.result
        assert params is not None
        kind, index = self.focus
        is_hidden = kind == "hidden"
        weights = params.hidden_weights[index] if is_hidden else params.output_weights[index]
        bias = params.hidden_bias[index] if is_hidden else params.output_bias[index]
        values = self.demo.inputs if is_hidden else (None if result is None else result.hidden_activations)
        name = f"H{index + 1}" if is_hidden else f"Score da classe {CLASSES[index]}"
        axis.text(0, .92, name + " · clicar num neurónio para ver as suas contas", fontsize=16, color=TEAL, weight="bold")
        input_labels = [number(v) for v in values] if values is not None else ["h1", "h2"]
        equation = " + ".join(f"{v} × ({number(w)})" for v, w in zip(input_labels, weights))
        axis.text(0, .56, equation + f" + ({number(bias)})", fontsize=21, color=INK)
        is_visible = result is not None and (self.demo.stage >= Stage.HIDDEN_ONE + index if is_hidden else self.demo.stage >= Stage.SCORES)
        if is_visible:
            total = result.hidden_sums[index] if is_hidden else result.scores[index]
            output = f"ReLU({number(total)}) = {number(max(total, 0))}" if is_hidden else f"Score = {number(total)}"
            axis.text(0, .15, "Soma = " + number(total) + "     " + output, fontsize=22, color=TEAL, weight="bold")
        else:
            axis.text(0, .15, "Parâmetros inicializados. A passagem ainda não começou.", fontsize=17, color=MUTED)

    def _draw_probabilities(self) -> None:
        axis = self.detail_axis
        result = self.demo.result
        assert result is not None
        axis.text(0, .90, "Softmax considera os dois scores em conjunto", fontsize=17, color=TEAL, weight="bold")
        # GUI parameters lie in [-1,1], so raw exponentials are safe and match
        # the visible scores. The model uses the equivalent stable softmax.
        numerator = np.exp(result.scores)
        axis.text(0, .54, f"exp({number(result.scores[0])}) = {number(numerator[0])}   ·   exp({number(result.scores[1])}) = {number(numerator[1])}", fontsize=17)
        axis.text(0, .19, f"Dividir cada um pelo total {number(numerator.sum())}. Soma das probabilidades = 1.", fontsize=16)
        for index, value in enumerate(result.probabilities):
            y = .62 - index * .45
            axis.add_patch(Rectangle((.72, y), .16, .17, facecolor="#dce9ed", edgecolor="none"))
            axis.add_patch(Rectangle((.72, y), .16 * value, .17, facecolor=INPUT_COLORS[index], edgecolor="none"))
            axis.text(.68, y + .08, str(CLASSES[index]), fontsize=17, va="center", ha="right")
            axis.text(.90, y + .08, f"{value:.1%}".replace(".", ","), fontsize=16, va="center")

    def _draw_detail(self) -> None:
        axis = self.detail_axis
        axis.clear()
        axis.set_axis_off()
        if self.demo.stage >= Stage.SOFTMAX:
            self._draw_probabilities()
        elif self.demo.stage >= Stage.PARAMETERS:
            self._draw_neuron_detail()
        else:
            hints = ("A imagem UCI já tem 8×8 píxeis. Cada quadrado guarda uma intensidade.",
                     "A matriz representa o mesmo dígito. O valor 0 é claro e 16 é escuro.",
                     "Flatten conserva a ordem e os 64 valores. Clica na matriz ou no vetor para escolher um píxel.",
                     "Usamos só dois dos 64 píxeis. Dividimos cada valor por 16 para obter as entradas da rede.")
            axis.text(0, .88, hints[int(self.demo.stage)], fontsize=17, color=INK)
            if self.demo.stage >= Stage.FLATTEN:
                for slot, index in enumerate(self.demo.pixel_indices):
                    row, col = divmod(index, 8)
                    raw = self.demo.image[row, col]
                    value = "Valor de origem: " + number(raw) if self.demo.stage == Stage.FLATTEN else "Entrada normalizada: " + number(self.demo.inputs[slot])
                    axis.text(slot * .51, .40, f"Entrada {slot + 1}: linha {row + 1}, coluna {col + 1}\nPíxel {index + 1} no vetor. {value}",
                              fontsize=16, color=INPUT_COLORS[slot], linespacing=1.6)

    def render(self) -> None:
        """Draw only values available in the selected teaching stage."""
        stage = self.demo.stage
        self.heading.set_text(f"{int(stage) + 1}/10   {TITLES[int(stage)]}")
        self.status.set_text("Imagem → matriz → vetor de 64 valores → 2 entradas → rede 2–2–2 → probabilidades")
        if stage == Stage.RESULT:
            result = self.demo.result
            assert result is not None
            predicted = CLASSES[int(result.probabilities.argmax())]
            self.status.set_text(f"Previsão: {predicted}   ·   dígito real: {self.demo.labels[self.demo.example_index]}   ·   rede aleatória, ainda sem treino")
        self._draw_image()
        self.flow_dots, self.flow_paths = [], []
        self._draw_data_stage() if stage < Stage.PARAMETERS else self._draw_network()
        self._draw_detail()
        self.buttons[2].label.set_text("Pausar" if self.is_running else "Animar")
        self.pixel_button.label.set_text(f"Escolher entrada {self.input_slot + 1}")
        self.pixel_button.set_active(stage in (Stage.FLATTEN, Stage.INPUTS))
        self.pixel_button.ax.set_visible(stage in (Stage.FLATTEN, Stage.INPUTS))
        self.footer.set_text(f"2 dos 64 píxeis · classes 0 e 5 · parâmetros aleatórios · seed {self.demo.seed} · sem treino · valores no ecrã arredondados")
        self.figure.canvas.draw_idle()
