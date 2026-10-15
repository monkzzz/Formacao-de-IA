"""Presenter controls and live feedback for the Flappy Bird demonstration."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.backend_bases import CloseEvent, MouseEvent
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.widgets import Button

from .formato_pt import numero
from .ajuste_janela import fit_window
from .flappy_bird import FlappyLearner


class FlappyBirdInterface:
    """Keep learning, playback and presentation speed independently observable."""

    def __init__(self, animate: bool = True) -> None:
        self.learner = FlappyLearner()
        self.is_running = False
        self.training_target: int | None = None
        self.hold_frames = 0
        self.figure = plt.figure(figsize=(14, 8), facecolor="#f6fafb")
        fit_window(self.figure)
        self.figure.canvas.manager.set_window_title("Formação IA · Flappy Bird")
        self.figure.suptitle("Aprendizagem por reforço · Flappy Bird", fontsize=23, weight="bold", y=0.97)
        self.game = self.figure.add_axes((0.055, 0.29, 0.58, 0.58))
        self._create_game()
        self._create_feedback()
        self._create_controls()
        self.animation: FuncAnimation | None = None
        self.render()
        if animate:
            self.animation = FuncAnimation(
                self.figure, self.tick, init_func=self.render,
                interval=45, blit=False, cache_frame_data=False,
            )
        self.figure.canvas.mpl_connect("close_event", self._close)

    def _create_game(self) -> None:
        self.game.set(xlim=(0, 100), ylim=(60, 0), aspect="equal")
        self.game.set_facecolor("#e1f4f8")
        self.game.set_xticks([])
        self.game.set_yticks([])
        self.game.set_title("O pássaro observa o tubo e escolhe uma ação", fontsize=15, pad=14)
        self.pipes = [Rectangle((0, 0), 5, 1, facecolor="#008694", edgecolor="#005b65", lw=2) for _ in range(2)]
        for pipe in self.pipes:
            self.game.add_patch(pipe)
        self.bird = Circle((8, 30), 2, facecolor="#ed9836", edgecolor="#8d4d08", lw=1.5)
        self.eye = Circle((8.7, 29.3), 0.45, color="#172b33")
        self.beak = Polygon(((10, 29.5), (11, 30), (10, 30.5)), color="#d97941")
        for part in (self.bird, self.eye, self.beak):
            self.game.add_patch(part)
        self.game_status = self.game.text(50, 7, "", ha="center", fontsize=17, weight="bold", color="#172b33")
        self.event_text = self.game.text(50, 51, "", ha="center", fontsize=17, weight="bold")

    def _create_feedback(self) -> None:
        self.status = self.figure.text(0.69, 0.86, "", va="top", fontsize=14, linespacing=1.45, color="#172b33")
        # Below the eight status lines, so the chart title never touches «Acumulada no episódio».
        self.curve = self.figure.add_axes((0.71, 0.31, 0.25, 0.19))
        self.curve.set_title("Resultados reais do treino", fontsize=14)
        self.curve.set_xlabel("Episódios concluídos", fontsize=11)
        self.curve.set_ylabel("Tubos passados", fontsize=11)
        self.curve.grid(alpha=0.18)
        self.raw_line, = self.curve.plot([], [], color="#bfd9de", lw=1, label="Por episódio")
        self.mean_line, = self.curve.plot([], [], color="#008694", lw=2, label="Média dos últimos 20")
        self.curve.legend(fontsize=9, loc="upper left")
        self.figure.text(0.055, 0.24, "Recompensa: sobreviver +0,1  ·  passar um tubo +5  ·  colidir −10", fontsize=14, color="#005b65")
        self.figure.text(0.055, 0.19, "Observação → ação → recompensa → atualização da estratégia", fontsize=15, weight="bold")
        self.footer = self.figure.text(0.055, 0.025, "", fontsize=11, color="#52666d")

    def _create_controls(self) -> None:
        actions = (
            ("Iniciar", self.toggle_running), ("Um passo", self.single_step),
            ("Treinar +200", self.accelerate_training),
            ("Testar política", self.toggle_learning), ("Reiniciar", self.restart),
        )
        self.buttons: list[Button] = []
        for index, (label, callback) in enumerate(actions):
            axis = self.figure.add_axes((0.055 + index * 0.185, 0.095, 0.17, 0.06))
            button = Button(axis, label, color="#e1eff2", hovercolor="#c1e3e9")
            button.label.set_fontsize(12)
            button.on_clicked(callback)
            self.buttons.append(button)

    def toggle_running(self, event: MouseEvent | None = None) -> None:
        """Pause or resume without changing learned values or the current episode."""
        self.is_running = not self.is_running
        self.render()
        self.figure.canvas.draw_idle()

    def single_step(self, event: MouseEvent | None = None) -> None:
        """Pause and advance exactly one state/action/reward transition."""
        self.is_running = False
        self.training_target = None
        self.hold_frames = 0
        self.learner.advance()
        self.render()
        self.figure.canvas.draw_idle()

    def accelerate_training(self, event: MouseEvent | None = None) -> None:
        """Train another 200 episodes in bounded batches without blocking controls."""
        if not self.learner.is_learning:
            self.learner.set_learning(True)
        self.training_target = len(self.learner.scores) + 200
        self.is_running = True
        self.hold_frames = 0
        self.render()
        self.figure.canvas.draw_idle()

    def toggle_learning(self, event: MouseEvent | None = None) -> None:
        """Play the current policy with exploration and Q updates disabled, or resume training."""
        self.learner.set_learning(not self.learner.is_learning)
        self.training_target = None
        self.is_running = False
        self.hold_frames = 0
        self.render()
        self.figure.canvas.draw_idle()

    def restart(self, event: MouseEvent | None = None) -> None:
        """Reset this demonstration to its reproducible untrained initial state."""
        self.learner = FlappyLearner()
        self.is_running = False
        self.training_target = None
        self.hold_frames = 0
        self.render()
        self.figure.canvas.draw_idle()

    def tick(self, frame: int = 0) -> tuple[Artist, ...]:
        """Advance at most 160 transitions per frame, holding ordinary collisions visible."""
        if not self.is_running:
            return self.render()
        if self.hold_frames > 0:
            self.hold_frames -= 1
            return self.render()
        for _ in range(160 if self.training_target is not None else 1):
            self.learner.advance()
            if self.training_target is not None and len(self.learner.scores) >= self.training_target:
                self.training_target = None
                self.is_running = False
                break
            if self.learner.needs_reset and self.training_target is None:
                self.hold_frames = 12
                break
        return self.render()

    def _update_curve(self) -> None:
        scores = self.learner.scores
        episodes = np.arange(1, len(scores) + 1)
        cumulative = np.concatenate(([0.0], np.cumsum(scores)))
        starts = np.maximum(0, episodes - 20)
        means = (cumulative[episodes] - cumulative[starts]) / np.minimum(episodes, 20)
        self.raw_line.set_data(episodes, scores)
        self.mean_line.set_data(episodes, means)
        self.curve.set_xlim(0, max(20, len(scores) + 1))
        self.curve.set_ylim(0, max(2, max(scores, default=0) + 1))

    def _update_status(self) -> None:
        learner = self.learner
        mode = "TREINO · aprende" if learner.is_learning else "POLÍTICA · sem aprender"
        action = "—" if learner.last_action is None else ("Saltar ↑" if learner.last_action else "Não saltar")
        choice = "Exploração" if learner.was_exploration else "Tabela Q"
        if learner.last_action is None:
            choice = "À espera de uma ação"
        self.status.set_text(
            f"{mode}\nTreino: {len(learner.scores)} episódios concluídos\n"
            f"Exploração: {learner.epsilon:.0%} das decisões\n\n"
            f"Última ação: {action}\nEscolha: {choice}\n"
            f"Recompensa: {numero(learner.last_reward, '+.1f')}\n"
            f"Acumulada no episódio: {numero(learner.total_reward, '+.1f')}"
        )
        self.buttons[0].label.set_text("Pausar" if self.is_running else "Iniciar")
        self.buttons[3].label.set_text("Voltar ao treino" if not learner.is_learning else "Testar política")
        hint = "A política usa a tabela aprendida. Não altera os valores Q." if not learner.is_learning else "Dados simulados. A melhoria não é garantida em cada episódio."
        if self.training_target is not None:
            hint = f"Treino acelerado até {self.training_target} episódios; podes pausar a qualquer momento."
        self.footer.set_text(hint)

    def render(self) -> tuple[Artist, ...]:
        """Refresh existing artists, including the terminal scene, without advancing."""
        environment = self.learner.environment
        lower = environment.gap_y - environment.pipe_gap / 2
        upper = environment.gap_y + environment.pipe_gap / 2
        self.pipes[0].set_bounds(environment.pipe_x - 2.5, 0, 5, lower)
        self.pipes[1].set_bounds(environment.pipe_x - 2.5, upper, 5, environment.height - upper)
        self.bird.center = (environment.bird_x, environment.bird_y)
        self.eye.center = (environment.bird_x + 0.7, environment.bird_y - 0.7)
        self.beak.set_xy(((10, environment.bird_y - 0.5), (11, environment.bird_y), (10, environment.bird_y + 0.5)))
        self.game_status.set_text(f"Tubos passados: {environment.score}")
        message = self.learner.end_reason if self.learner.needs_reset else ""
        if self.learner.last_reward == 5.0:
            message = "Tubo ultrapassado: +5"
        self.event_text.set_text(message)
        self.event_text.set_color("#b94237" if environment.is_terminal else "#008694")
        self._update_curve()
        self._update_status()
        return (self.bird, self.eye, self.beak, *self.pipes, self.status, self.game_status, self.event_text, self.raw_line, self.mean_line)

    def _close(self, event: CloseEvent) -> None:
        if self.animation is not None and self.animation.event_source is not None:
            self.animation.event_source.stop()
