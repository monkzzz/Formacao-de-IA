"""Unit tests for the four consolidated machine-learning exercises."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

EXERCISE_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "modulo1"
)
sys.path.insert(0, str(EXERCISE_DIRECTORY))


def load_exercise_module(file_name: str, module_name: str):
    """Import an exercise whose filename starts with a numeric lesson number."""
    spec = importlib.util.spec_from_file_location(module_name, EXERCISE_DIRECTORY / file_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


paradigms = load_exercise_module("dia1_modulo1_01_paradigmas_aprendizagem.py", "paradigms_exercise")
forward_pass = load_exercise_module("dia1_modulo1_02_forward_pass_mlp.py", "forward_exercise")
learning = load_exercise_module("dia1_modulo1_03_perda_backpropagation_otimizacao.py", "learning_exercise")
metrics = load_exercise_module("dia1_modulo1_04_metricas_avaliacao.py", "metrics_exercise")


class ParadigmTests(unittest.TestCase):
    def test_logistic_regression_separates_sessions(self) -> None:
        sessions, labels = paradigms.make_labelled_sessions()
        weights, bias = paradigms.fit_logistic_regression(sessions, labels)
        predictions = paradigms.predict_purchase(sessions, weights, bias)
        self.assertGreater((predictions == labels).mean(), 0.9)

    def test_flappy_bird_environment_returns_valid_states(self) -> None:
        environment = paradigms.FlappyBird(seed=4)
        state = environment.reset()
        next_state, reward, done = environment.step(1)

        self.assertEqual(len(state), 3)
        self.assertEqual(len(next_state), 3)
        self.assertIn(reward, (0.1, 5.0, -10.0))
        self.assertIsInstance(done, bool)

    def test_q_learning_returns_a_two_action_policy(self) -> None:
        q_table, scores = paradigms.train_flappy_bird(episodes=10)

        self.assertEqual(q_table.shape, (12, 20, 4, 2))
        self.assertEqual(len(scores), 10)
        self.assertTrue(np.isfinite(q_table).all())


class ForwardPassTests(unittest.TestCase):
    def test_manual_neuron_matches_matrix_product(self) -> None:
        image = np.arange(64, dtype=np.float64).reshape(8, 8) / 4.0
        parameters = forward_pass.init_weights()
        result = forward_pass.forward(image, *parameters)
        total, _ = forward_pass.single_neuron(result.inputs, parameters[0][0], parameters[1][0])
        self.assertAlmostEqual(total, result.hidden_sums[0])
        self.assertAlmostEqual(result.probabilities.sum(), 1.0)


class LearningTests(unittest.TestCase):
    def test_backprop_matches_numerical_gradient(self) -> None:
        random = np.random.default_rng(0)
        features = random.random((5, 64))
        labels = np.array((0, 3, 5, 7, 9))
        analytic, numeric = learning.finite_difference_check(
            learning.init_network(), features, labels
        )
        self.assertAlmostEqual(analytic, numeric, places=6)

    def test_gradient_descent_reduces_loss(self) -> None:
        random = np.random.default_rng(1)
        features = random.random((40, 64))
        labels = random.integers(0, 10, 40)
        _, losses, _ = learning.train(features, labels, 0.3, steps=30)
        self.assertLess(losses[-1], losses[0])


class MetricTests(unittest.TestCase):
    def test_confusion_counts_and_scores(self) -> None:
        result = metrics.binary_metrics(np.array((1, 1, 0, 0)), np.array((1, 0, 1, 0)))
        self.assertEqual(
            (result.true_positives, result.false_positives,
             result.false_negatives, result.true_negatives),
            (1, 1, 1, 1),
        )
        self.assertAlmostEqual(result.f1, 0.5)

    def test_perfect_scores_have_unit_auc(self) -> None:
        *_, auc = metrics.roc_curve(np.array((0, 0, 1, 1)), np.array((0.1, 0.2, 0.8, 0.9)))
        self.assertAlmostEqual(auc, 1.0)


if __name__ == "__main__":
    unittest.main()
