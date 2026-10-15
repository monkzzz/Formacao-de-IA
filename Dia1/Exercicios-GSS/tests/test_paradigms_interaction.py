"""Regression tests for learning feedback and presenter controls."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
import numpy as np

from tests.test_ml_core_exercises import paradigms
from apoio.flappy_bird import FlappyBird, FlappyLearner
from apoio.flappy_bird_ui import FlappyBirdInterface


def click_button(figure: plt.Figure, axis: plt.Axes) -> None:
    """Send real canvas events through a button's registered callbacks."""
    figure.canvas.draw()
    x, y = axis.transAxes.transform((0.5, 0.5))
    for name in ("button_press_event", "button_release_event"):
        event = MouseEvent(name, figure.canvas, x, y, button=1)
        figure.canvas.callbacks.process(name, event)


class FlappyFeedbackTests(unittest.TestCase):
    def test_flap_moves_up_in_screen_coordinates(self) -> None:
        environment = FlappyBird()
        initial_y = environment.bird_y
        environment.step(1)
        self.assertLess(environment.bird_y, initial_y)

    def test_collision_does_not_reward_or_count_a_pipe(self) -> None:
        environment = FlappyBird()
        environment.pipe_x = 11
        environment.bird_y = environment.gap_y + 13
        _, reward, done = environment.step(0)
        self.assertTrue(done)
        self.assertEqual(reward, -10)
        self.assertEqual(environment.score, 0)
        with self.assertRaisesRegex(RuntimeError, "terminou"):
            environment.step(0)

    def test_safe_trailing_edge_crossing_rewards_once(self) -> None:
        environment = FlappyBird()
        environment.pipe_x = 6
        environment.bird_y = environment.gap_y
        _, reward, done = environment.step(0)
        self.assertFalse(done)
        self.assertEqual(reward, 5)
        self.assertEqual(environment.score, 1)
        _, reward, _ = environment.step(0)
        self.assertEqual(reward, 0.1)
        self.assertEqual(environment.score, 1)

    def test_pipe_behind_bird_cannot_cause_a_pipe_collision(self) -> None:
        environment = FlappyBird()
        environment.pipe_x = 0
        environment.passed = True
        environment.bird_y = environment.gap_y + 14
        _, _, done = environment.step(0)
        self.assertFalse(done)

    def test_terminal_update_does_not_bootstrap_and_keeps_collision_scene(self) -> None:
        learner = FlappyLearner()
        learner.q_table.fill(10)
        learner.environment.bird_y = 2
        learner.environment.velocity = -4
        learner.state = learner.environment.observe()
        previous_state = learner.state
        learner.advance()
        self.assertTrue(learner.needs_reset)
        self.assertTrue(learner.environment.is_terminal)
        self.assertLess(learner.environment.bird_y, 2)
        self.assertEqual(len(learner.scores), 1)
        self.assertEqual(learner.q_table[previous_state + (learner.last_action,)], 6)

    def test_policy_playback_keeps_q_values_and_training_history_frozen(self) -> None:
        learner = FlappyLearner()
        for _ in range(30):
            learner.advance()
        previous_q = learner.q_table.copy()
        previous_scores = learner.scores.copy()
        learner.set_learning(False)
        for _ in range(100):
            learner.advance()
        np.testing.assert_array_equal(learner.q_table, previous_q)
        self.assertEqual(learner.scores, previous_scores)
        self.assertEqual(learner.epsilon, 0)
        self.assertFalse(learner.was_exploration)
        self.assertGreater(len(learner.policy_scores), 0)

    def test_training_is_reproducible(self) -> None:
        first_q, first_scores = paradigms.train_flappy_bird(20, seed=7)
        second_q, second_scores = paradigms.train_flappy_bird(20, seed=7)
        np.testing.assert_array_equal(first_q, second_q)
        self.assertEqual(first_scores, second_scores)


class PresenterControlsTests(unittest.TestCase):
    def tearDown(self) -> None:
        plt.close("all")

    def test_training_and_new_session_use_canvas_callbacks_without_retraining(self) -> None:
        interface = paradigms.SessionLearningInterface()
        self.assertFalse(interface.is_trained)
        click_button(interface.figure, interface.buttons[0].ax)
        self.assertTrue(interface.is_trained)
        previous_weights = interface.weights.copy()
        previous_data = interface.sessions.copy()
        x, y = interface.axes[1].transData.transform((5, 30))
        event = MouseEvent("button_press_event", interface.figure.canvas, x, y, button=1)
        interface.figure.canvas.callbacks.process(event.name, event)
        np.testing.assert_allclose(interface.new_session, (5, 0.3), atol=0.03)
        self.assertIn("prevê", interface.status.get_text())
        self.assertIn("atribui ao Grupo", interface.status.get_text())
        np.testing.assert_array_equal(interface.weights, previous_weights)
        np.testing.assert_array_equal(interface.sessions, previous_data)

    def test_changing_group_count_preserves_supervised_model_and_reset_clears_input(self) -> None:
        interface = paradigms.SessionLearningInterface()
        interface.train()
        previous_weights = interface.weights.copy()
        interface.next_example()
        click_button(interface.figure, interface.buttons[2].ax)
        self.assertEqual(interface.cluster_count, 3)
        self.assertEqual(interface.centers.shape, (3, 2))
        np.testing.assert_array_equal(interface.weights, previous_weights)
        interface.reset()
        self.assertFalse(interface.is_trained)
        self.assertIsNone(interface.new_session)

    def test_game_stays_paused_until_started_and_step_advances_once(self) -> None:
        interface = FlappyBirdInterface(animate=False)
        interface.tick()
        self.assertEqual(interface.learner.steps, 0)
        click_button(interface.figure, interface.buttons[1].ax)
        self.assertEqual(interface.learner.steps, 1)
        self.assertFalse(interface.is_running)
        self.assertTrue(interface.game.yaxis_inverted())
        click_button(interface.figure, interface.buttons[3].ax)
        self.assertFalse(interface.learner.is_learning)
        click_button(interface.figure, interface.buttons[4].ax)
        self.assertTrue(interface.learner.is_learning)
        self.assertEqual(len(interface.learner.scores), 0)

    def test_accelerated_training_stops_at_requested_episode_count(self) -> None:
        interface = FlappyBirdInterface(animate=False)
        interface.accelerate_training()
        for _ in range(200):
            interface.tick()
            if not interface.is_running:
                break
        self.assertEqual(len(interface.learner.scores), 200)
        self.assertIsNone(interface.training_target)
        self.assertFalse(interface.is_running)

    def test_noninteractive_entry_point_does_not_open_or_wait(self) -> None:
        with patch.dict(os.environ, {"FORMACAO_ML_NO_PAUSE": "1"}), patch.object(plt, "show") as show:
            paradigms.main()
        show.assert_not_called()
        self.assertEqual(plt.get_fignums(), [])


class SessionModelBoundaryTests(unittest.TestCase):
    def test_constant_or_nonfinite_attributes_are_rejected(self) -> None:
        for features in (np.ones((3, 2)), np.array(((0, 1), (np.nan, 2)))):
            with self.assertRaises(ValueError):
                paradigms.fit_kmeans(features, 2)

    def test_final_groups_match_final_centers_even_after_one_iteration(self) -> None:
        sessions, _ = paradigms.make_labelled_sessions()
        groups, centers = paradigms.fit_kmeans(sessions, 3, iterations=1)
        np.testing.assert_array_equal(groups, paradigms.assign_groups(sessions, centers, sessions.std(axis=0)))


if __name__ == "__main__":
    unittest.main()
