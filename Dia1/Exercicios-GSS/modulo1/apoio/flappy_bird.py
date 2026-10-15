"""Deterministic Flappy Bird environment and inspectable tabular Q-learning."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

SEED = 12
State = tuple[int, int, int]
QTable = NDArray[np.float64]


@dataclass
class FlappyBird:
    """Use screen coordinates: y grows downwards, so a flap has negative speed."""

    seed: int = SEED
    width: int = 100
    height: int = 60
    pipe_gap: int = 26
    bird_x: int = 8
    bird_radius: int = 2
    pipe_width: int = 5

    def __post_init__(self) -> None:
        self.random = np.random.default_rng(self.seed)
        self.reset()

    def reset(self) -> State:
        """Start a fresh episode while retaining the seeded environment sequence."""
        self.bird_y = self.height // 2
        self.velocity = 0
        self.pipe_x = self.width - 12
        self.gap_y = self._next_gap()
        self.score = 0
        self.passed = False
        self.is_terminal = False
        return self.observe()

    def _next_gap(self) -> int:
        margin = self.pipe_gap // 2 + self.bird_radius
        return int(self.random.integers(margin, self.height - margin + 1))

    def observe(self) -> State:
        """Return bounded bins for distance, vertical offset and speed."""
        distance = int(np.clip((self.pipe_x - self.bird_x) // 8, 0, 11))
        offset = int(np.clip((self.bird_y - self.gap_y + self.height) // 6, 0, 19))
        speed = int(np.clip((self.velocity + 3) // 2, 0, 3))
        return distance, offset, speed

    def _has_collision(self) -> bool:
        touches_pipe = abs(self.pipe_x - self.bird_x) <= (
            self.pipe_width / 2 + self.bird_radius
        )
        outside_gap = abs(self.bird_y - self.gap_y) + self.bird_radius > self.pipe_gap / 2
        outside_world = not self.bird_radius <= self.bird_y <= self.height - self.bird_radius
        return outside_world or (touches_pipe and outside_gap)

    def step(self, action: int) -> tuple[State, float, bool]:
        """Move once; collision overrides reward and only safe crossings score."""
        if action not in (0, 1):
            raise ValueError("A ação deve ser 0 (não saltar) ou 1 (saltar).")
        if self.is_terminal:
            raise RuntimeError("O episódio terminou; chama reset() antes de avançar.")
        self.velocity = min(4, (-4 if action else self.velocity) + 1)
        self.bird_y += self.velocity
        self.pipe_x -= 3
        self.is_terminal = self._has_collision()
        if self.is_terminal:
            return self.observe(), -10.0, True
        reward = 0.1
        # Reward a full crossing only after the trailing pipe edge clears the bird.
        if self.pipe_x + self.pipe_width / 2 < self.bird_x - self.bird_radius and not self.passed:
            self.passed = True
            self.score += 1
            reward = 5.0
        if self.pipe_x < -5:
            self.pipe_x = self.width - 12
            self.gap_y = self._next_gap()
            self.passed = False
        return self.observe(), reward, False


class FlappyLearner:
    """Advance one transition at a time, retaining terminal frames and feedback."""

    def __init__(self, seed: int = SEED) -> None:
        self.seed = seed
        self.environment = FlappyBird(seed)
        self.random = np.random.default_rng(seed + 100)
        self.q_table: QTable = np.zeros((12, 20, 4, 2))
        self.scores: list[int] = []
        self.policy_scores: list[int] = []
        self.is_learning = True
        self._start_episode()

    @property
    def epsilon(self) -> float:
        """Exploration decreases during training and is disabled for policy playback."""
        return max(0.05, 0.9 * np.exp(-len(self.scores) / 220)) if self.is_learning else 0.0

    def _start_episode(self) -> None:
        self.state = self.environment.reset()
        self.steps = 0
        self.total_reward = 0.0
        self.needs_reset = False
        self.last_action: int | None = None
        self.last_reward = 0.0
        self.was_exploration = False
        self.end_reason = ""

    def set_learning(self, is_learning: bool) -> None:
        """Switch mode, discard the partial episode and keep learned Q-values."""
        self.is_learning = is_learning
        self._start_episode()

    def advance(self) -> None:
        """Apply one action and update Q only in training mode."""
        if self.needs_reset:
            self._start_episode()
        self.was_exploration = self.is_learning and self.random.random() < self.epsilon
        self.last_action = int(self.random.integers(2)) if self.was_exploration else int(
            self.q_table[self.state].argmax()
        )
        next_state, reward, done = self.environment.step(self.last_action)
        self.steps += 1
        self.last_reward = reward
        self.total_reward += reward
        if self.is_learning:
            # Bootstrap a time-limited episode, but never bootstrap a collision.
            target = reward + (0.0 if done else 0.9 * self.q_table[next_state].max())
            index = self.state + (self.last_action,)
            self.q_table[index] += 0.2 * (target - self.q_table[index])
        self.state = next_state
        self.needs_reset = done or self.steps >= 500
        if self.needs_reset:
            self.end_reason = "Colisão" if done else "Limite de 500 passos"
            history = self.scores if self.is_learning else self.policy_scores
            history.append(self.environment.score)


def train_flappy_bird(episodes: int = 80, seed: int = SEED) -> tuple[QTable, list[int]]:
    """Train a bounded number of episodes with the same transition engine as the UI."""
    if not isinstance(episodes, int) or episodes < 1:
        raise ValueError("episodes deve ser um inteiro positivo.")
    learner = FlappyLearner(seed)
    while len(learner.scores) < episodes:
        learner.advance()
    return learner.q_table.copy(), learner.scores.copy()
