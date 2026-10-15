"""Presenter-controlled metrics with sample tracing, threshold and ROC."""
from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import KeyEvent, MouseEvent
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from matplotlib.widgets import Button, Slider
from .formato_pt import numero
from .ajuste_janela import fit_window
from .evaluation_metrics import BinaryMetrics, MetricScenario, binary_metrics, metric_scenarios, roc_curve, safe_divide

TEAL, ORANGE, BLUE, INK = "#008694", "#c76d1b", "#436987", "#172b33"
COLORS = {"TP": TEAL, "FN": ORANGE, "FP": BLUE, "TN": "#a7bdc4"}
GROUP_LABELS = {"TP": "Defeito detetado", "FN": "Defeito que escapou",
                "FP": "Falso alarme", "TN": "Conforme bem identificada"}
TITLES = ("As respostas conhecidas", "Do score à decisão", "Contar acertos e erros",
          "Taxa de acerto · accuracy", "Precisão · precision",
          "Sensibilidade · recall", "F1 · combinar precisão e sensibilidade",
          "Quanto custam os erros?", "ROC e AUC · comparar limiares")
# The numerator is a subset of the reference population; F1 uses doubled TP
# contributions rather than a proportion of distinct pieces.
METRIC_GROUPS = {3: ("TP", "FN", "FP", "TN"), 4: ("TP", "FP"),
                 5: ("TP", "FN"), 6: ("TP", "FP", "FN"), 7: ("FN", "FP")}


class MetricsInterface:
    """Reveal calculations without modifying samples or training a model."""

    def __init__(self) -> None:
        self.scenarios = metric_scenarios()
        self.scenario_index = self.stage = 0
        self.threshold = .5
        self.is_baseline = self.is_running = False
        self.is_fn_expensive = True
        self.group: str | None = None
        self.sample: int | None = None
        self.figure = plt.figure(figsize=(16, 9), facecolor="#f6fafb")
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Métricas de avaliação")
        self.heading = self.figure.text(.045, .94, "", fontsize=24, weight="bold", color=INK)
        self.status = self.figure.text(.045, .884, "", fontsize=14, color=TEAL)
        self.samples_axis = self.figure.add_axes((.055, .38, .38, .43))
        self.result_axis = self.figure.add_axes((.53, .38, .40, .43))
        self.detail = self.figure.text(.055, .30, "", fontsize=16, color=INK, va="top", linespacing=1.4)
        self.legend_axis = self.figure.add_axes((.055, .335, .88, .035))
        self.footer = self.figure.text(.045, .025, "", fontsize=11, color="#52666d")
        self.buttons: list[Button] = []
        self._controls()
        self.timer = self.figure.canvas.new_timer(interval=1800)
        self.timer.add_callback(self.tick)
        self.figure.canvas.mpl_connect("button_press_event", self.select)
        self.figure.canvas.mpl_connect("key_press_event", self.on_key)
        self.figure.canvas.mpl_connect("close_event", lambda _: self.pause())
        self.render()

    @property
    def scenario(self) -> MetricScenario:
        """Current immutable example."""
        return self.scenarios[self.scenario_index]

    @property
    def predictions(self) -> np.ndarray:
        """The baseline predicts conforme regardless of the threshold."""
        return (np.zeros_like(self.scenario.labels) if self.is_baseline else
                (self.scenario.scores >= self.threshold).astype(np.int64))

    @property
    def metrics(self) -> BinaryMetrics:
        """Compute counts from the same visible samples."""
        return binary_metrics(self.scenario.labels, self.predictions)

    def _controls(self) -> None:
        actions = (("← Anterior", self.previous), ("Próximo →", self.advance),
                   ("Animar", self.animate), ("Outro cenário", self.next_scenario),
                   ("Sempre conforme", self.baseline), ("Trocar custos", self.costs),
                   ("Reiniciar", self.reset))
        for i, (name, callback) in enumerate(actions):
            button = Button(self.figure.add_axes((.045 + i * .133, .065, .122, .055)), name,
                            color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(11)
            button.on_clicked(callback)
            self.buttons.append(button)
        self.slider = Slider(self.figure.add_axes((.16, .145, .65, .024)), "Limiar", 0, 1,
                             valinit=.5, valstep=.01, valfmt="%.2f", color=TEAL)
        self.slider._format = lambda value: numero(value, ".2f")  # noqa: SLF001 - decimal comma on the slider
        self.slider.valtext.set_text(numero(self.slider.val, ".2f"))
        self.slider.on_changed(self.set_threshold)

    def pause(self) -> None:
        """Stop playback, preserving the current stage."""
        self.is_running = False
        self.timer.stop()

    def advance(self, _event=None) -> None:
        """Reveal the next calculation."""
        self.pause()
        self.stage = min(self.stage + 1, len(TITLES) - 1)
        self.group = self.sample = None
        self.render()

    def previous(self, _event=None) -> None:
        """Revisit calculations with unchanged scores."""
        self.pause()
        self.stage = max(0, self.stage - 1)
        self.group = self.sample = None
        self.render()

    def animate(self, _event=None) -> None:
        """Pause/resume reveal, stopping at ROC."""
        if self.is_running:
            self.pause()
        elif self.stage < len(TITLES) - 1:
            self.is_running = True
            self.timer.start()
        self.render()

    def tick(self) -> None:
        """Advance only while playback is active."""
        if not self.is_running:
            return
        self.stage = min(self.stage + 1, len(TITLES) - 1)
        self.group = self.sample = None
        if self.stage == len(TITLES) - 1:
            self.pause()
        self.render()

    def next_scenario(self, _event=None) -> None:
        """Change the fixed example and restart its explanation."""
        self.pause()
        self.scenario_index = (self.scenario_index + 1) % len(self.scenarios)
        self.stage = 0
        self.is_baseline = False
        self.group = self.sample = None
        self.slider.set_val(.5)
        self.render()

    def baseline(self, _event=None) -> None:
        """Compare with always predicting the negative class."""
        self.pause()
        self.is_baseline = not self.is_baseline
        self.group = self.sample = None
        self.render()

    def costs(self, _event=None) -> None:
        """Swap illustrative costs, preserving the predictions."""
        self.is_fn_expensive = not self.is_fn_expensive
        self.render()

    def reset(self, _event=None) -> None:
        """Restore the first example and default controls."""
        self.pause()
        self.scenario_index = self.stage = 0
        self.is_baseline = False
        self.is_fn_expensive = True
        self.group = self.sample = None
        self.slider.set_val(.5)
        self.render()

    def set_threshold(self, value: float) -> None:
        """Change decisions while keeping scores fixed."""
        self.pause()
        self.threshold = float(value)
        self.group = None
        self.render()

    def on_key(self, event: KeyEvent) -> None:
        """Use arrows, Space and R as in previous demonstrations."""
        callback = {"right": self.advance, "left": self.previous,
                    " ": self.animate, "r": self.reset}.get(event.key)
        if callback:
            callback()

    def _groups(self) -> np.ndarray:
        return np.where(self.scenario.labels == 1,
                        np.where(self.predictions == 1, "TP", "FN"),
                        np.where(self.predictions == 1, "FP", "TN"))

    def select(self, event: MouseEvent) -> None:
        """Trace confusion cells to samples, or inspect a sample score."""
        if event.button != 1 or event.xdata is None or event.ydata is None:
            return
        if event.inaxes is self.result_axis and self.stage == 2:
            col, row = int(np.floor(event.xdata + .5)), int(np.floor(event.ydata + .5))
            if col in (0, 1) and row in (0, 1):
                self.group = (("TP", "FN"), ("FP", "TN"))[row][col]
                self.sample = None
        elif event.inaxes is self.samples_axis:
            if self.stage == 1:
                y = self.scenario.labels + .10*np.sin(np.arange(len(self.scenario.labels)))
                distances = (self.scenario.scores-event.xdata)**2+(y-event.ydata)**2
                self.sample, self.group = int(distances.argmin()), None
            else:
                col, row = int(round(event.xdata)), int(round(event.ydata))
                index = row * 10 + col
                if 0 <= col < 10 and row >= 0 and index < len(self.scenario.labels):
                    self.sample, self.group = index, None
        self.render()

    def _draw_samples(self) -> None:
        axis = self.samples_axis
        axis.clear()
        axis.set_axis_on()
        if self.stage == 1:
            axis.set_position((.14,.38,.32,.43))
            self._draw_score_decisions()
            return
        axis.set_position((.055,.38,.38,.43))
        groups = self._groups()
        for i, label in enumerate(self.scenario.labels):
            color = COLORS[groups[i]] if self.stage >= 2 else (ORANGE if label else "#a7bdc4")
            focus = (self.group,) if self.group else METRIC_GROUPS.get(self.stage)
            alpha = .13 if focus and groups[i] not in focus else 1
            axis.scatter(i % 10, i // 10, s=220, color=color, alpha=alpha,
                         edgecolor=INK if label else "white", linewidth=1.5)
            if self.scenario.labels.size == 8:
                axis.text(i, .55, f"{i+1}\n{numero(self.scenario.scores[i], '.2f')}",
                          ha="center", fontsize=13, alpha=alpha)
        rows = max(2, int(np.ceil(len(self.scenario.labels) / 10)))
        axis.set(xlim=(-.8, 9.8), ylim=(rows, -1), aspect="equal")
        axis.set_axis_off()
        title = {3: "Taxa de acerto: considerar todas as peças",
                 4: "Precisão: considerar só as peças sinalizadas",
                 5: "Sensibilidade: considerar só os defeitos reais",
                 6: "F1: deteções, falsos alarmes e defeitos perdidos",
                 7: "Custo: considerar apenas os erros"}.get(
                     self.stage, "Cada ponto é uma peça · contorno escuro: defeito real")
        axis.set_title(title, fontsize=14, pad=18)
        if self.sample is not None:
            i = self.sample
            axis.scatter(i % 10, i // 10, s=380, facecolors="none", edgecolors="#e4ab00", lw=3)

    def _draw_score_decisions(self) -> None:
        axis = self.samples_axis
        axis.set_aspect("auto")
        y = self.scenario.labels + .10*np.sin(np.arange(len(self.scenario.labels)))
        axis.scatter(self.scenario.scores, y, s=110, color=[ORANGE if label else BLUE for label in self.scenario.labels])
        if not self.is_baseline:
            axis.axvline(self.threshold, color=TEAL, lw=3)
            axis.axvspan(self.threshold, 1, color=TEAL, alpha=.08)
        axis.set(xlim=(-.03, 1.03), ylim=(-.4,1.4), yticks=(0,1),
                 yticklabels=("Conforme real","Defeito real"), xlabel="Score fixo de cada peça")
        axis.set_title("À direita do limiar: sinalizar defeito", fontsize=15)
        axis.grid(axis="x", alpha=.15)
        axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: numero(value, ".1f")))
        if self.sample is not None:
            i=self.sample
            axis.scatter(self.scenario.scores[i],y[i],s=240,facecolors="none",edgecolors="#e4ab00",lw=3)

    def _draw_confusion(self) -> None:
        axis, m = self.result_axis, self.metrics
        axis.clear()
        axis.set_axis_on()
        counts = ((m.true_positives, m.false_negatives), (m.false_positives, m.true_negatives))
        axis.set(xlim=(-.5, 1.5), ylim=(1.5, -.5), aspect="equal")
        axis.set_xticks((0, 1), ("Previsto: defeito", "Previsto: conforme"), fontsize=14)
        axis.set_yticks((0, 1), ("Real: defeito", "Real: conforme"), fontsize=14)
        axis.xaxis.tick_top()
        for row in range(2):
            for col in range(2):
                name = (("TP", "FN"), ("FP", "TN"))[row][col]
                axis.add_patch(Rectangle((col-.5, row-.5), 1, 1, facecolor=COLORS[name], alpha=.16))
                axis.text(col, row-.12, str(counts[row][col]), ha="center", va="center", fontsize=36)
                axis.text(col, row+.16, name, ha="center", fontsize=18, color=COLORS[name], weight="bold")
                label = "Conforme bem\nidentificada" if name == "TN" else GROUP_LABELS[name]
                axis.text(col, row+.35, label, ha="center", va="center", fontsize=11, color=INK)
        axis.tick_params(length=0)
        axis.set_title("Clica numa célula para destacar as peças", fontsize=14, pad=45)

    def _draw_legend(self) -> None:
        axis = self.legend_axis
        axis.clear()
        axis.set_axis_off()
        if self.stage < 2:
            return
        counts = self._counts()
        for i, group in enumerate(("TP", "FP", "FN", "TN")):
            x = i * .25
            axis.scatter(x + .008, .5, s=65, color=COLORS[group])
            axis.text(x + .025, .5, f"{group} {counts[group]} · {GROUP_LABELS[group]}",
                      va="center", fontsize=11, color=INK)
        axis.set(xlim=(0, 1), ylim=(0, 1))

    def _counts(self) -> dict[str, int]:
        m = self.metrics
        return {"TP": m.true_positives, "FP": m.false_positives,
                "FN": m.false_negatives, "TN": m.true_negatives}

    def _prepare_card(self) -> None:
        axis = self.result_axis
        axis.clear()
        axis.set_aspect("auto")
        axis.set_axis_off()
        axis.set(xlim=(0, 1), ylim=(0, 1))
        axis.add_patch(Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="#d4e3e7"))

    def _draw_metric(self) -> None:
        self._prepare_card()
        axis, m, counts = self.result_axis, self.metrics, self._counts()
        total = len(self.scenario.labels)
        cards = {
            3: ("Quantas decisões estão certas?", "Todas as peças entram no denominador.",
                r"\frac{TP+TN}{TP+FP+FN+TN}", counts["TP"] + counts["TN"], total,
                m.accuracy, f"{counts['TP'] + counts['TN']} decisões certas em {total} peças."),
            4: ("Dos alarmes, quantos são verdadeiros?", "Olhar apenas para as peças sinalizadas como defeito.",
                r"\frac{TP}{TP+FP}", counts["TP"], counts["TP"] + counts["FP"],
                m.precision, f"{counts['TP']} defeitos reais em {counts['TP'] + counts['FP']} alarmes."),
            5: ("Dos defeitos reais, quantos detetámos?", "Olhar apenas para as peças que têm defeito.",
                r"\frac{TP}{TP+FN}", counts["TP"], counts["TP"] + counts["FN"],
                m.recall, f"{counts['TP']} detetados em {counts['TP'] + counts['FN']} defeitos reais."),
            6: ("Detetar bem e evitar falsos alarmes?", "F1 combina precisão e sensibilidade numa só medida.",
                r"\frac{2\times TP}{2\times TP+FP+FN}", 2 * counts["TP"],
                2 * counts["TP"] + counts["FP"] + counts["FN"], m.f1,
                "Média harmónica: uma medida baixa limita o F1."),
        }
        question, scope, formula, numerator, denominator, value, reading = cards[self.stage]
        axis.text(.05, .91, question, fontsize=18, weight="bold", color=TEAL, va="top")
        axis.text(.05, .79, scope, fontsize=12, color=INK)
        axis.text(.5, .62, f"${formula}$", fontsize=26, ha="center", va="center", color=INK)
        axis.text(.22, .38, rf"$\frac{{{numerator}}}{{{denominator}}}$", fontsize=30,
                  ha="center", va="center", color=INK)
        axis.text(.42, .38, "=" if denominator else "→", fontsize=26, va="center", color=INK)
        axis.text(.68, .38, numero(value, ".1%"), fontsize=37, weight="bold",
                  ha="center", va="center", color=TEAL)
        if denominator == 0:
            reading = "A medida não está definida: não há casos.\nA demonstração apresenta 0 por convenção."
        axis.text(.5, .20, reading, fontsize=13, ha="center", va="center", color=INK)
        self._draw_metric_bar(counts)

    def _draw_metric_bar(self, counts: dict[str, int]) -> None:
        groups = METRIC_GROUPS[self.stage]
        weights = [counts[group] * (2 if self.stage == 6 and group == "TP" else 1) for group in groups]
        total, x = sum(weights), .06
        for group, weight in zip(groups, weights):
            width = .88 * safe_divide(weight, total)
            self.result_axis.add_patch(Rectangle((x, .075), width, .035,
                                                facecolor=COLORS[group]))
            x += width

    def _draw_cost(self) -> None:
        self._prepare_card()
        axis, counts = self.result_axis, self._counts()
        fn_cost, fp_cost = (10, 1) if self.is_fn_expensive else (1, 10)
        axis.text(.05, .91, "Os dois erros têm o mesmo impacto?", fontsize=18,
                  weight="bold", color=TEAL, va="top")
        for y, group, cost in ((.70, "FN", fn_cost), (.45, "FP", fp_cost)):
            axis.text(.05, y, GROUP_LABELS[group], fontsize=15, color=COLORS[group], weight="bold")
            pieces = "peça" if counts[group] == 1 else "peças"
            units = "unidade" if cost == 1 else "unidades"
            axis.text(.05, y - .10, f"{counts[group]} {pieces} × {cost} {units} = {counts[group] * cost}",
                      fontsize=22, color=INK)
        axis.text(.05, .15, f"Custo total: {counts['FN'] * fn_cost + counts['FP'] * fp_cost}",
                  fontsize=30, color=TEAL, weight="bold")
        axis.text(.05, .05, "Unidades fictícias · usa «Trocar custos» para comparar.", fontsize=12, color=INK)

    def _draw_roc(self) -> None:
        axis = self.result_axis
        # Reserve space below the plot for the formula in its x-axis label;
        # it must not overlap the shared piece legend.
        axis.set_position((.53, .42, .40, .39))
        axis.clear()
        axis.set_axis_on()
        axis.set_aspect("auto")
        axis.xaxis.tick_bottom()
        scores = np.zeros_like(self.scenario.scores) if self.is_baseline else self.scenario.scores
        fpr, tpr, auc = roc_curve(self.scenario.labels, scores)
        axis.plot(fpr, tpr, color=TEAL, lw=2.5, label=f"AUC = {numero(auc, '.3f')}")
        axis.fill_between(fpr, tpr, color=TEAL, alpha=.10)
        axis.plot((0, 1), (0, 1), "--", color="#a7bdc4", label="Ordenação ao acaso")
        m = self.metrics
        axis.scatter(safe_divide(m.false_positives, m.false_positives + m.true_negatives),
                     m.recall, color=ORANGE, s=110, zorder=4, label="Decisão atual")
        axis.set(xlim=(-.02, 1.02), ylim=(-.02, 1.02),
                 xlabel="Falsos alarmes / conformes reais · FP / (FP + TN)",
                 ylabel="Sensibilidade · TP / (TP + FN)")
        axis.set_title("O limiar percorre a curva; não treina o modelo", fontsize=15)
        axis.grid(alpha=.2)
        axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: numero(value, ".1f")))
        axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: numero(value, ".1f")))
        axis.legend(loc="lower right", fontsize=11)

    def _explanation(self) -> str:
        m = self.metrics
        total = len(self.scenario.labels)
        text = (
            f"{total} peças fictícias. {int(self.scenario.labels.sum())} têm defeito.\nAs respostas conhecidas permitem avaliar as previsões.",
            f"Sinalizar quando score ≥ {numero(self.threshold, '.2f')}. Os scores ficam fixos.\nMudar o limiar altera a decisão, sem alterar os pesos de um modelo.",
            "TP: defeito detetado. FN: defeito que escapou.\nFP: falso alarme. TN: peça conforme corretamente identificada.",
            "Acerto global: soma os defeitos detetados e as peças conformes bem identificadas.\nExperimenta «Classes raras» e «Sempre conforme»: 98% de acerto pode esconder todos os defeitos.",
            "Precisão: TP / (TP + FP). As peças esbatidas não entram nesta conta.\nUm falso alarme aumenta o denominador, sem aumentar os defeitos detetados.",
            "Sensibilidade: TP / (TP + FN). As peças conformes não entram nesta conta.\nUm defeito que escapa aumenta o denominador, sem aumentar os defeitos detetados.",
            f"Precisão {numero(m.precision, '.1%')} · sensibilidade {numero(m.recall, '.1%')} → F1 {numero(m.f1, '.1%')}.\nA barra representa 2 × TP + FP + FN; TP conta duas vezes. F1 não inclui TN nem os custos.",
            "A mesma matriz pode ter custos diferentes: muda «Trocar custos» e depois o limiar.\nEscolher custos e limiar exige validação e conhecimento do problema real.",
            "Melhor ordenação: curva mais perto do canto superior esquerdo. AUC mede a área sob a curva.\nAUC = 0,5: referência ao acaso; AUC = 1: ordenação perfeita neste exemplo. Não é taxa de acerto.",
        )
        if self.sample is not None:
            i = self.sample
            real = "defeito" if self.scenario.labels[i] else "conforme"
            predicted = "defeito" if self.predictions[i] else "conforme"
            return (f"Peça {i+1}: real {real}, score {numero(self.scenario.scores[i], '.3f')}.\n" +
                    (f"Previsto {predicted}: {self._groups()[i]}." if self.stage >= 1 else "Avança para revelar a decisão."))
        if self.is_baseline and self.stage == 1:
            return "Sempre conforme: todas as previsões são negativas.\nO limiar fica desativado enquanto usamos este baseline."
        return text[self.stage]

    def render(self) -> None:
        """Show only the current teaching stage with counts from visible samples."""
        self.heading.set_text(f"{self.stage+1}/{len(TITLES)}   {TITLES[self.stage]}")
        mode = "sempre conforme" if self.is_baseline else f"limiar {numero(self.threshold, '.2f')}"
        self.status.set_text(f"{self.scenario.name} · {mode} · dados e scores fictícios, fixos")
        self.result_axis.set_position((.53, .38, .40, .43))
        self._draw_samples()
        if self.stage == len(TITLES) - 1:
            self._draw_roc()
        elif self.stage == 7:
            self._draw_cost()
        elif self.stage in (3, 4, 5, 6):
            self._draw_metric()
        elif self.stage == 2:
            self._draw_confusion()
        else:
            self.result_axis.clear()
            self.result_axis.set_axis_off()
            self.result_axis.text(.05, .65, "Resposta real + previsão\npermitem contar os erros.", fontsize=25, color=TEAL)
            if self.stage == 1:
                self.result_axis.text(.05, .3, f"{int(self.predictions.sum())} peças sinalizadas", fontsize=26, color=ORANGE)
        self.detail.set_text(self._explanation())
        self._draw_legend()
        self.slider.set_active(self.stage >= 1 and not self.is_baseline)
        self.buttons[2].label.set_text("Pausar" if self.is_running else "Animar")
        self.buttons[4].label.set_text("Usar scores" if self.is_baseline else "Sempre conforme")
        self.footer.set_text("Exemplo didático · sem treino nem teste · divisão por zero apresentada como 0 · setas / Espaço / R")
        self.figure.canvas.draw_idle()
