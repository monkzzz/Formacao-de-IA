"""Visual walkthrough from digit pixels to training, evaluation and drawing."""
from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import KeyEvent, MouseEvent
from matplotlib.patches import Circle
from matplotlib.widgets import Button, Slider
from .formato_pt import numero
from .ajuste_janela import fit_window
from .digit_training_demo import DigitTrainingDemo

TEAL, ORANGE, INK = "#008694", "#c76d1b", "#172b33"
TITLES = ("Separar dados antes de treinar", "Imagem, matriz e 64 entradas",
          "Rede inicial: 64–32–10", "Um batch: forward pass", "Um batch: calcular a perda",
          "Um batch: backpropagation", "Um batch: atualizar pesos e bias",
          "Repetir o treino e observar validação", "Avaliação final no teste reservado",
          "Usar a rede: desenhar um dígito")
# The same training-cycle strip as exercise 03; stages outside the cycle leave it muted.
PHASES = ("Forward pass", "Perda", "Backpropagation", "Otimização", "Repetir")
STAGE_PHASE = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4}


class DigitTrainingInterface:
    """Train on CPU in short timer callbacks; preserve the final test boundary."""

    def __init__(self, demo: DigitTrainingDemo) -> None:
        self.demo = demo
        self.stage = self.neuron = 0
        self.revealed_phases: set[int] = set()
        self.is_running = False
        self.target_epoch = 0
        self.selected_test_indices = np.array([], dtype=np.int64)
        self.test_sample = 0
        self.drawing = np.zeros((demo.api.DRAWING_SIZE, demo.api.DRAWING_SIZE))
        self.last_point: tuple[float, float] | None = None
        self.draw_probabilities: np.ndarray | None = None
        self.drawing_label: int | None = None
        self.is_inspecting_weights = False
        self.weight_pixel = 2
        self.notice = ""
        self.figure = plt.figure(figsize=(16, 9), facecolor="#f6fafb")
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Classificador de dígitos")
        self.heading = self.figure.text(.045, .94, "", fontsize=24, weight="bold", color=INK)
        self.status = self.figure.text(.045, .884, "", fontsize=14, color=TEAL)
        self.phase_texts = [self.figure.text(.655 + index * .078, .888, phase, fontsize=11, ha="center",
                                             bbox={"boxstyle": "round,pad=.35", "edgecolor": "none"})
                            for index, phase in enumerate(PHASES)]
        self.image_axis = self.figure.add_axes((.045, .425, .22, .37))
        self.main_axis = self.figure.add_axes((.32, .425, .29, .37))
        self.result_axis = self.figure.add_axes((.69, .425, .275, .37))
        self.detail = self.figure.text(.045, .35, "", fontsize=16, va="top", linespacing=1.5, color=INK)
        self.footer = self.figure.text(.045, .025, "", fontsize=11, color="#52666d")
        self.buttons: list[Button] = []
        self._controls()
        self.timer = self.figure.canvas.new_timer(interval=180)
        self.timer.add_callback(self.tick)
        self.figure.canvas.mpl_connect("button_press_event", self.press)
        self.figure.canvas.mpl_connect("motion_notify_event", self.motion)
        self.figure.canvas.mpl_connect("button_release_event", self.release)
        self.figure.canvas.mpl_connect("key_press_event", self.on_key)
        self.figure.canvas.mpl_connect("close_event", lambda _: self.pause())
        self.render()

    def _controls(self) -> None:
        actions = (("← Anterior", self.previous), ("Próximo →", self.advance),
                   ("Próximo batch", self.next_batch), ("Treinar +12", self.train),
                   ("Outra imagem", self.next_image), ("Avaliar teste", self.evaluate),
                   ("Desenhar", self.use), ("Reiniciar", self.reset))
        for i, (label, callback) in enumerate(actions):
            button = Button(self.figure.add_axes((.045 + i*.116, .062, .108, .052)), label,
                            color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(11)
            button.on_clicked(callback)
            self.buttons.append(button)
        self.neuron_slider = Slider(self.figure.add_axes((.13, .147, .30, .02)), "Neurónio", 1, 32,
                                    valinit=1, valstep=1, valfmt="%d", color=TEAL)
        self.neuron_slider.on_changed(self.set_neuron)
        self.infer_button = Button(self.figure.add_axes((.68, .136, .13, .043)), "Inferir",
                                   color="#e1eff2", hovercolor="#c1e3e9")
        self.infer_button.on_clicked(self.infer)
        self.clear_button = Button(self.figure.add_axes((.83, .136, .13, .043)), "Limpar",
                                   color="#e1eff2", hovercolor="#c1e3e9")
        self.clear_button.on_clicked(self.clear)
        self.weights_button = Button(self.figure.add_axes((.47, .136, .16, .043)), "Ver pesos",
                                   color="#e1eff2", hovercolor="#c1e3e9")
        self.weights_button.on_clicked(self.inspect_weights)

    def inspect_weights(self, _event=None) -> None:
        """Compare weights and the fixed validation prediction with the initial model."""
        self.is_inspecting_weights = not self.is_inspecting_weights
        self.render()

    def pause(self) -> None:
        """Pause training, preserving parameters and the remaining epoch target."""
        self.is_running = False
        self.timer.stop()

    def advance(self, _event=None) -> None:
        """Reveal one stage, executing each demonstration phase only once."""
        self.pause()
        target = min(self.stage + 1, 9)
        if target == 8:
            self.evaluate()
            return
        if 3 <= target <= 6 and target not in self.revealed_phases:
            self.demo.advance_phase()
            self.revealed_phases.add(target)
        self.stage = target
        self.notice = ""
        self.render()

    def previous(self, _event=None) -> None:
        """Revisit rendered results without applying another update."""
        self.pause()
        self.stage = max(0, self.stage - 1)
        self.notice = ""
        self.render()

    def next_batch(self, _event=None) -> None:
        """Repeat the cycle step by step: forward pass of the next batch, then «Próximo»."""
        self.pause()
        if self.demo.is_frozen:
            return
        # A half-shown batch is completed first, so no computed step is ever discarded.
        has_finished_batch = self.demo.phase != 0
        while self.demo.phase != 0:
            self.demo.advance_phase()
        self.demo.advance_phase()
        self.revealed_phases = {3}
        self.stage = 3
        self.notice = "O batch anterior foi concluído com a sua atualização." if has_finished_batch else ""
        self.render()

    def train(self, _event=None) -> None:
        """Train twelve more epochs with pause/resume and one epoch per callback."""
        if self.demo.is_frozen:
            return
        if self.is_running:
            self.pause()
        else:
            if self.target_epoch <= self.demo.epoch:
                self.target_epoch = self.demo.epoch + self.demo.api.EPOCHS
            self.is_running = True
            self.stage = 7
            self.revealed_phases.update(range(3, 7))
            self.timer.start()
        self.render()

    def tick(self) -> None:
        """Perform a short CPU epoch, update curves and stop at the requested total."""
        if not self.is_running:
            return
        try:
            self.demo.train_epoch()
        except Exception as error:
            self.pause()
            self.notice = f"Treino interrompido: {error}"
            self.render()
            raise
        if self.demo.epoch >= self.target_epoch:
            self.pause()
        self.notice = ""
        self.render()

    def evaluate(self, _event=None) -> None:
        """Freeze the validation-selected checkpoint before showing any test metric."""
        self.pause()
        try:
            self.demo.evaluate_test()
        except RuntimeError as error:
            self.notice = str(error)
            self.render()
            return
        self.stage = 8
        self.revealed_phases.update(range(3, 7))
        errors = np.flatnonzero(self.demo.test_labels != self.demo.test_predictions)
        self.selected_test_indices = errors if len(errors) else np.arange(len(self.demo.test_labels))
        self.test_sample = 0
        self.notice = ""
        self.render()

    def use(self, _event=None) -> None:
        """Use the frozen final model for a new drawing."""
        self.pause()
        if not self.demo.is_frozen:
            self.notice = "Conclui o treino e avalia o modelo antes de desenhar."
        else:
            self.stage = 9
            self.notice = ""
        self.render()

    def next_image(self, _event=None) -> None:
        """Change an inspection image without learning from it."""
        if self.stage == 8:
            if len(self.selected_test_indices):
                self.test_sample = (self.test_sample + 1) % len(self.selected_test_indices)
        elif self.stage < 8:
            self.demo.next_validation_example()
        elif self.stage == 9:
            self.demo.next_validation_example()
            self.drawing = np.repeat(np.repeat(self.demo.validation_image,3,axis=0),3,axis=1).copy()
            self.drawing_label = self.demo.validation_digit
            self.draw_probabilities = None
            self.notice = f"Exemplo UCI de validação: dígito {self.demo.validation_digit}. Clica em Inferir ou edita o desenho."
        self.render()

    def reset(self, _event=None) -> None:
        """Restore seed 23 and clear the demo, checkpoint, test and drawing state."""
        self.pause()
        self.demo.reset()
        self.stage = self.target_epoch = self.neuron = 0
        self.revealed_phases.clear()
        self.is_inspecting_weights = False
        self.neuron_slider.set_val(1)
        self.drawing.fill(0)
        self.draw_probabilities = None
        self.drawing_label = None
        self.selected_test_indices = np.array([], dtype=np.int64)
        self.notice = ""
        self.render()

    def set_neuron(self, value: float) -> None:
        """Inspect one hidden unit's actual weights or gradients."""
        self.neuron = int(value) - 1
        self.render()

    def on_key(self, event: KeyEvent) -> None:
        """Control stages and training from the keyboard."""
        callback = {"right": self.advance, "left": self.previous, " ": self.train,
                    "r": self.reset, "t": self.train}.get(event.key)
        if callback:
            callback()

    def _canvas_point(self, event: MouseEvent) -> tuple[float, float] | None:
        size = self.demo.api.DRAWING_SIZE
        if event.inaxes is not self.image_axis or event.xdata is None or event.ydata is None:
            return None
        return (float(np.clip(event.xdata, 0, size-1)), float(np.clip(event.ydata, 0, size-1)))

    def press(self, event: MouseEvent) -> None:
        """Paint a stroke or select a confusion-matrix cell."""
        if event.button != 1:
            return
        if self.stage == 9:
            self.last_point = self._canvas_point(event)
            if self.last_point is not None:
                self._paint(self.last_point)
        elif self.stage == 8 and event.inaxes is self.main_axis:
            self._select_confusion(event)
        elif event.inaxes is self.main_axis and self.stage in (2,7) and self.is_inspecting_weights:
            if event.xdata is not None and event.ydata is not None:
                col, row = int(np.floor(event.xdata+.5)), int(np.floor(event.ydata+.5))
                if 0 <= col < 8 and 0 <= row < 8:
                    self.weight_pixel = row*8+col
                    self.render()

    def motion(self, event: MouseEvent) -> None:
        """Interpolate ink while dragging on the drawing canvas."""
        if self.stage == 9 and self.last_point is not None and event.button == 1:
            point = self._canvas_point(event)
            if point is not None:
                self._paint(point)

    def release(self, _event=None) -> None:
        """Finish a stroke even if it ends outside the canvas."""
        self.last_point = None

    def _paint(self, point: tuple[float, float]) -> None:
        self.demo.api.draw_segment(self.drawing, self.last_point, point)
        self.last_point = point
        self.draw_probabilities = None
        self.drawing_label = None
        self.notice = "Desenho alterado. Clica em Inferir para atualizar a previsão."
        self.render()

    def infer(self, _event=None) -> None:
        """Infer only for a nonempty drawing with the frozen final model."""
        if self.stage != 9 or not self.demo.is_frozen:
            return
        if not np.any(self.drawing):
            self.notice = "Desenha um dígito antes de pedir a inferência."
        else:
            image = self.demo.api.downsample_drawing(self.drawing)
            _, self.draw_probabilities = self.demo.inspect(image)
            self.notice = "Inferência: pesos fixos. Escrita livre pode diferir dos exemplos UCI."
        self.render()

    def clear(self, _event=None) -> None:
        """Clear the canvas and stale prediction."""
        self.drawing.fill(0)
        self.draw_probabilities = None
        self.drawing_label = None
        self.last_point = None
        self.notice = ""
        self.render()

    def _select_confusion(self, event: MouseEvent) -> None:
        if event.xdata is None or event.ydata is None:
            return
        predicted, real = int(np.floor(event.xdata+.5)), int(np.floor(event.ydata+.5))
        if not (0 <= real < 10 and 0 <= predicted < 10):
            return
        self.selected_test_indices = np.flatnonzero(
            (self.demo.test_labels == real) & (self.demo.test_predictions == predicted))
        self.test_sample = 0
        self.notice = f"Real {real}, previsto {predicted}: {len(self.selected_test_indices)} imagens."
        self.render()

    def _draw_image(self) -> None:
        axis = self.image_axis
        axis.clear()
        axis.set_axis_on()
        if self.stage == 9:
            size = self.demo.api.DRAWING_SIZE
            axis.imshow(self.drawing, cmap="gray_r", vmin=0, vmax=16, extent=(0, size, size, 0))
            axis.set_title(f"Exemplo UCI · real {self.drawing_label}" if self.drawing_label is not None
                           else "Desenha com o botão esquerdo", fontsize=15)
            axis.set_xticks(range(0, size+1, 3)); axis.set_yticks(range(0, size+1, 3))
            axis.grid(alpha=.2)
            return
        if self.stage == 8:
            if not len(self.selected_test_indices):
                axis.set_axis_off()
                axis.text(.05, .5, "Nenhuma imagem\nnesta célula", fontsize=20)
                return
            index = self.selected_test_indices[self.test_sample]
            image = self.demo.test_images[index]
            title = f"Teste · real {self.demo.test_labels[index]}\nprevisto {self.demo.test_predictions[index]}"
        elif self.stage in (3,4,5,6) and self.demo.batch_indices is not None:
            index = self.demo.train_indices[int(self.demo.batch_indices[0])]
            image, title = self.demo.images[index], f"Treino · 1.ª imagem do batch\nreal {self.demo.labels[index]}"
        else:
            image, title = self.demo.validation_image, f"Validação · dígito real {self.demo.validation_digit}"
        axis.imshow(image, cmap="gray_r", vmin=0, vmax=16, interpolation="nearest")
        axis.set_title(title, fontsize=15, pad=12)
        axis.set_xticks([]); axis.set_yticks([])
        if self.stage == 1:
            for (row, col), value in np.ndenumerate(image):
                axis.text(col, row, str(int(value)), ha="center", va="center", fontsize=10,
                          color="white" if value >= 9 else INK)

    def _probabilities(self, probabilities: np.ndarray, initial: np.ndarray | None = None,
                       label: int | None = None) -> None:
        """Softmax bars; with a known label its bar is orange, as the target in exercise 03."""
        axis = self.result_axis
        axis.clear(); axis.set_axis_on()
        axis.set_aspect("auto")
        colors = [ORANGE if digit == label else TEAL for digit in range(10)]
        if initial is not None:
            axis.bar(np.arange(10)-.18, initial, width=.36, color="#a7bdc4", label="Antes")
        axis.bar(np.arange(10)+(.18 if initial is not None else 0), probabilities,
                 width=.36 if initial is not None else .7, color=colors, label="Depois")
        digit = int(probabilities.argmax())
        axis.set(xticks=range(10), ylim=(0, 1), xlabel="Classe", ylabel="Probabilidade")
        if label is None:
            title = f"Previsão {digit} · {numero(probabilities[digit], '.1%')}"
        elif initial is None:
            title = f"Previsão {digit} · p({label}) = {numero(probabilities[label], '.1%')}"
        else:
            title = f"p({label}): {numero(initial[label], '.1%')} → {numero(probabilities[label], '.1%')}"
        axis.set_title(title, fontsize=15)
        if label is not None:
            axis.get_xticklabels()[label].set(color=ORANGE, fontweight="bold")
        axis.grid(axis="y", alpha=.2)
        if initial is not None:
            axis.legend(fontsize=10)

    def _batch_losses(self) -> None:
        """Loss of every image in the batch; the batch loss is their mean."""
        d, axis = self.demo, self.main_axis
        axis.clear(); axis.set_axis_on()
        axis.set_aspect("auto")
        losses = d.sample_losses
        axis.bar(range(len(losses)), losses, width=1, color="#a7bdc4")
        if len(losses):
            # Wider and in front, so the image shown on the left stays visible among 128 bars.
            axis.bar(0, losses[0], width=max(2, len(losses) / 40), color=ORANGE, zorder=3)
            axis.axhline(d.last_loss, color=TEAL, lw=2, label=f"média = {numero(d.last_loss, '.3f')}")
            axis.legend(fontsize=11, loc="lower right")
        axis.set(xlim=(-3, max(1, len(losses)) + 1), ylim=(0, 1.15 * max(1e-6, float(losses.max(initial=0)))),
                 xlabel="Imagens do batch (laranja: a 1.ª)", ylabel="−ln p(classe real)")
        axis.set_title("Perda de cada imagem do batch", fontsize=13)

    def _score_gradients(self) -> None:
        """Backpropagation starts at the scores: ∂L/∂s = p − y for the first image."""
        d, axis = self.demo, self.result_axis
        axis.clear(); axis.set_axis_on()
        axis.set_aspect("auto")
        target = np.eye(10)[d.sample_label]
        gradient = d.sample_probabilities - target
        axis.bar(range(10), gradient, color=[ORANGE if digit == d.sample_label else "#e2b48a" for digit in range(10)])
        axis.axhline(0, color=INK, lw=.8)
        axis.set(xticks=range(10), ylim=(-1, 1), xlabel="Classe", ylabel="p − y")
        axis.get_xticklabels()[d.sample_label].set(color=ORANGE, fontweight="bold")
        axis.set_title(f"Gradiente dos scores · real {d.sample_label}", fontsize=15)
        axis.grid(axis="y", alpha=.2)

    def _network(self) -> None:
        axis = self.main_axis
        axis.clear(); axis.set_axis_off()
        positions = [(x, y) for x, count in ((0, 6), (2, 6), (4, 10)) for y in np.linspace(0, 4, count)]
        for x in (0, 2):
            for y in np.linspace(0, 4, 6):
                for z in np.linspace(0, 4, 6 if x == 0 else 10):
                    axis.plot((x, x+2), (y, z), color="#a7bdc4", alpha=.3, lw=.7)
        for x, y in positions:
            axis.add_patch(Circle((x, y), .12, color=TEAL))
        axis.set(xlim=(-.4, 4.5), ylim=(-.5, 4.6), aspect="equal")
        axis.set_title("64 entradas · 32 ReLU · 10 scores\nSó parte das unidades desenhadas", fontsize=14)

    def _heatmap(self, matrix: np.ndarray, title: str) -> None:
        axis = self.main_axis
        axis.clear(); axis.set_axis_on()
        limit = max(float(np.abs(matrix).max()), 1e-6)
        axis.imshow(matrix, cmap="coolwarm", vmin=-limit, vmax=limit)
        axis.set_xticks([]); axis.set_yticks([])
        axis.set_title(title+"\nazul: negativo · vermelho: positivo", fontsize=14)

    def _curves(self) -> None:
        epochs = range(len(self.demo.history))
        for axis, title, attrs in ((self.main_axis, "Perda média por época", ("train_loss", "validation_loss")),
                                  (self.result_axis, "Accuracy por época", ("train_accuracy", "validation_accuracy"))):
            axis.clear(); axis.set_axis_on()
            axis.set_aspect("auto")
            if axis is self.main_axis and self.demo.batch_history:
                # Each repeated cycle adds a point at once; the epoch means come only at epoch ends.
                positions, losses = zip(*self.demo.batch_history)
                axis.plot(positions, losses, ".", color="#a7bdc4", markersize=5, label="Cada batch (treino)")
            for attr, label, color in zip(attrs, ("Treino", "Validação"), (TEAL, ORANGE)):
                axis.plot(epochs, [getattr(m, attr) for m in self.demo.history], "o-", color=color, label=label)
            last = self.demo.batch_history[-1][0] if self.demo.batch_history else 0
            right = max(1, self.demo.epoch, last)
            # Margins keep the epoch-0 point and the first batches off the axis borders.
            axis.set(title=title, xlabel="Época", xlim=(-.04 * right, 1.04 * right))
            axis.grid(alpha=.2); axis.legend(fontsize=10)
        top = max([m.train_loss for m in self.demo.history] + [m.validation_loss for m in self.demo.history]
                  + [loss for _, loss in self.demo.batch_history])
        self.main_axis.set_ylim(0, 1.1 * top)
        self.result_axis.set_ylim(0, 1.05)

    def _test_results(self) -> None:
        confusion = self.demo.test_result[0]
        axis = self.main_axis
        axis.clear(); axis.set_axis_on()
        axis.imshow(confusion, cmap="Blues")
        axis.set(xticks=range(10), yticks=range(10), xlabel="Previsto", ylabel="Real")
        axis.set_title("Clica numa confusão para ver imagens", fontsize=14)
        for (row, col), count in np.ndenumerate(confusion):
            axis.text(col, row, str(count), ha="center", va="center", fontsize=11,
                      color="white" if count > confusion.max()/2 else INK)
        tp = confusion.diagonal()
        denominator = confusion.sum(axis=0) + confusion.sum(axis=1)
        f1 = np.divide(2*tp, denominator, out=np.zeros(10), where=denominator != 0)
        self.result_axis.clear(); self.result_axis.set_axis_on()
        self.result_axis.bar(range(10), f1, color=TEAL)
        self.result_axis.set(xticks=range(10), ylim=(0, 1), xlabel="Classe", ylabel="F1")
        self.result_axis.set_title("F1 por classe · macro: média das 10", fontsize=14)

    def _draw_main(self) -> None:
        d, stage = self.demo, self.stage
        _, probabilities = d.inspect(d.validation_image)
        _, initial = d.inspect(d.validation_image, initial=True)
        self._probabilities(initial if stage == 2 else probabilities, initial if stage == 7 else None)
        if stage == 0:
            self.main_axis.clear(); self.main_axis.set_axis_off()
            self.main_axis.text(0, .9, f"Treino: {len(d.train_indices)}\n\nValidação: {len(d.validation_indices)}\n\nTeste reservado: {len(d.test_labels)}", fontsize=23, va="top", color=TEAL)
            self.result_axis.clear(); self.result_axis.set_axis_off()
            self.result_axis.text(0, .9, "Treino ajusta parâmetros.\n\nValidação escolhe checkpoint.\n\nTeste mede no final.", fontsize=20, va="top")
        elif stage == 1:
            self.main_axis.clear(); self.main_axis.set_axis_on()
            self.main_axis.imshow(d.validation_image.reshape(1,64)/16, cmap="gray_r", vmin=0, vmax=1,
                                  extent=(-.5,63.5,.4,.6), aspect="auto")
            self.main_axis.set(yticks=[], xticks=(0, 7, 15, 31, 47, 63), xticklabels=(1, 8, 16, 32, 48, 64))
            self.main_axis.set_ylim(0,1)
            self.main_axis.set_title("Flatten por linhas · dividir por 16", fontsize=15)
            self.result_axis.clear(); self.result_axis.set_axis_off()
            self.result_axis.text(0,.75,"64 valores normalizados\n\nMesma ordem no treino\ne na inferência",fontsize=22,color=TEAL)
        elif stage == 2:
            if self.is_inspecting_weights:
                self._show_weights(initial=True)
            else:
                self._network()
        elif stage == 3:
            self.main_axis.clear(); self.main_axis.set_axis_on()
            self.main_axis.set_aspect("auto")
            self.main_axis.bar(range(32), d.sample_hidden, color=TEAL)
            self.main_axis.set_title("ReLU · 32 ativações da 1.ª imagem do batch", fontsize=13)
            self.main_axis.set_xlabel("Neurónio oculto")
            self._probabilities(d.sample_probabilities, label=d.sample_label)
        elif stage == 4:
            self._batch_losses()
            self._probabilities(d.sample_probabilities, label=d.sample_label)
        elif stage in (5, 6):
            values = d.last_gradient if stage == 5 else d.last_delta
            self._heatmap(values[self.neuron].numpy().reshape(8,8),
                          f"{'Gradientes' if stage == 5 else 'Atualização Δw'} · neurónio {self.neuron+1}")
            if stage == 5:
                self._score_gradients()
            else:
                # Both values were stored at this batch, so revisiting shows this update only.
                self._probabilities(d.sample_after, d.sample_probabilities, label=d.sample_label)
        elif stage == 7:
            if self.is_inspecting_weights:
                self._show_weights()
                self._probabilities(probabilities, initial)
            else:
                self._curves()
        elif stage == 8:
            self._test_results()
        elif stage == 9:
            self.main_axis.clear(); self.main_axis.set_axis_on()
            self.main_axis.imshow(d.api.downsample_drawing(self.drawing), cmap="gray_r", vmin=0, vmax=16)
            self.main_axis.set(xticks=[], yticks=[], title="24×24 reduzido a 8×8 · 64 entradas")
            if self.draw_probabilities is not None:
                self._probabilities(self.draw_probabilities)
            else:
                self.result_axis.clear(); self.result_axis.set_axis_off()
                self.result_axis.text(0, .5, "Desenha e clica em Inferir", fontsize=22, color=TEAL)

    def _show_weights(self, initial: bool = False) -> None:
        d = self.demo
        model = d.initial_model if initial else (d.final_model if d.is_frozen else d.model)
        weights = model.hidden_layer.weight[self.neuron].detach().numpy().reshape(8,8)
        bias = float(model.hidden_layer.bias[self.neuron].detach())
        self._heatmap(weights, f"64 pesos · neurónio {self.neuron+1} · bias {numero(bias, '.3f')}")

    def _explanation(self) -> str:
        d = self.demo
        if self.stage in (2,7) and self.is_inspecting_weights:
            model = d.initial_model if self.stage == 2 else (d.final_model if d.is_frozen else d.model)
            w = model.hidden_layer.weight[self.neuron].detach().numpy()
            bias = float(model.hidden_layer.bias[self.neuron].detach())
            x = d.validation_image.reshape(64)/16
            index = self.weight_pixel
            z = float(w @ x + bias)
            return (f"Píxel {index+1}: x={numero(x[index], '.4f')}, peso={numero(w[index], '.4f')}, contributo={numero(x[index]*w[index], '.4f')}. Clica noutro peso para o inspecionar.\n"
                    f"Neurónio {self.neuron+1}: soma dos 64 contributos + bias {numero(bias, '.4f')} = {numero(z, '.4f')}. ReLU={numero(max(0,z), '.4f')}.")
        if self.stage == 8:
            _, acc, precision, recall, f1, loss = d.test_result
            return (f"Checkpoint da época {d.best_epoch}. Teste: accuracy {numero(acc, '.1%')}, precision macro {numero(precision, '.3f')}, recall macro {numero(recall, '.3f')}.\n"
                    f"F1 macro {numero(f1, '.3f')} · cross-entropy {numero(loss, '.3f')}. Modelo fixado. O teste não altera pesos nem escolhe opções.")
        first_loss = float(d.sample_losses[0]) if len(d.sample_losses) else 0.0
        batches_per_epoch = int(np.ceil(len(d.train_features) / d.api.BATCH_SIZE))
        # cursor 0 after an update means an epoch has just ended: report its last batch.
        batches_done = int(np.ceil(d.cursor / d.api.BATCH_SIZE)) if d.cursor else (batches_per_epoch if d.updates else 0)
        epoch_label = d.epoch + 1 if d.cursor or not d.updates else d.epoch
        explanations = (
            "Dataset UCI · imagens 8×8, intensidades 0..16. Validação retirada apenas do treino oficial.\nO teste não é medido durante o treino. A imagem à esquerda pertence à validação.",
            "A matriz e o vetor contêm os mesmos 64 valores, na mesma ordem por linhas.\nA escala fixa 0..16 permite normalizar por 16, tanto no treino como na inferência.",
            "Pesos e bias inicializados aleatoriamente, seed 23. Probabilidades da imagem de validação, ainda sem treino.\nO exercício02 usou 2–2–2 para seguir as contas. Agora usamos todos os 64 píxeis e as 10 classes.",
            f"Forward do batch de {len(d.batch_indices) if d.batch_indices is not None else 0} imagens de treino. Ainda sem atualizar parâmetros.\nA imagem, as 32 ativações e as probabilidades pertencem à primeira imagem desse batch.",
            f"1.ª imagem (real {d.sample_label}): −ln p({d.sample_label}) = −ln {numero(d.sample_probabilities[d.sample_label], '.4f')} = {numero(first_loss, '.4f')}.\n"
            f"Cross-entropy do batch = média das {len(d.sample_losses)} perdas = {numero(d.last_loss, '.4f')}. É esta média que vamos derivar.",
            f"A backpropagation começa nos scores: p − y. A classe real fica negativa: subir esse score baixa a perda.\n"
            f"loss.backward() leva o gradiente até aos pesos. Norma nos pesos ocultos: {numero(d.gradient_norm, '.4f')}. Os parâmetros ainda não mudaram.",
            f"SGD: novo = atual −0,1 × gradiente. Norma da alteração dos pesos ocultos: {numero(d.weight_change, '.4f')}.\nTodos os pesos e bias atualizados em conjunto. Este mapa mostra apenas os 64 pesos do neurónio escolhido.",
            f"Batch {batches_done} de {batches_per_epoch} da época {epoch_label} · {d.updates} atualizações · melhor validação: época {d.best_epoch}, perda {numero(d.best_loss, '.4f')}.\n"
            "«Próximo batch» repete o ciclo passo a passo. «Treinar +12» repete-o em 12 épocas. «Avaliar teste» fixa o melhor checkpoint.",
            "",
            "Inferência com o checkpoint escolhido pela validação. Desenha, observa a redução 8×8 e clica em Inferir.\nOs pesos ficam fixos. «Exemplo UCI» permite comparar com uma imagem de validação.",
        )
        return explanations[self.stage]

    def _draw_phases(self) -> None:
        current = STAGE_PHASE.get(self.stage)
        for index, text in enumerate(self.phase_texts):
            is_current = index == current
            text.set_color("white" if is_current else "#52666d")
            text.set_fontweight("bold" if is_current else "normal")
            text.get_bbox_patch().set_facecolor(ORANGE if is_current and index in (1, 2, 3) else
                                                TEAL if is_current else "#e1eff2")

    def render(self) -> None:
        """Draw the current state without training or consulting new test results."""
        d = self.demo
        self.heading.set_text(f"{self.stage+1}/10   {TITLES[self.stage]}")
        self.status.set_text(f"Rede 64–32–10 · época {d.epoch} · {d.updates} atualizações · " +
                             ("modelo fixado" if d.is_frozen else "teste reservado"))
        self._draw_phases()
        self._draw_image()
        self._draw_main()
        self.detail.set_text(self.notice + "\n" + self._explanation() if self.notice else self._explanation())
        self.buttons[2].set_active(not d.is_frozen)
        self.buttons[3].set_active(not d.is_frozen)
        self.buttons[3].label.set_text("Pausar" if self.is_running else
                                     ("Retomar" if self.target_epoch > d.epoch else "Treinar +12"))
        self.buttons[4].label.set_text("Exemplo UCI" if self.stage == 9 else "Outra imagem")
        self.neuron_slider.ax.set_visible(self.stage in (5,6) or (self.stage in (2,7) and self.is_inspecting_weights))
        self.weights_button.ax.set_visible(self.stage in (2,7))
        self.weights_button.label.set_text("Ver rede" if self.stage == 2 and self.is_inspecting_weights else
                                          ("Ver curvas" if self.is_inspecting_weights else "Ver pesos"))
        for control in (self.infer_button, self.clear_button):
            control.ax.set_visible(self.stage == 9)
        self.footer.set_text("CPU · SGD 0,1 · seed 23 · treino/validação separados · teste final uma vez · setas / T / Espaço / R")
        self.figure.canvas.draw_idle()
