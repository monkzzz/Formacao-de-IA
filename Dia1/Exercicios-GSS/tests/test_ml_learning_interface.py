"""Check every small-network gradient, update ordering and actual GUI interactions."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tests.test_ml_core_exercises import learning
from tests.test_ml_forward_interface import click, examples
from apoio import digit_dataset
from apoio.forward_pass_demo import DemoParameters, initialize_parameters, run_forward
from apoio.learning_demo import (
    LearningDemo, LearningStage as Stage, calculate_step,
    cross_entropy_scores, parameter_arrays, target_vector,
)
from apoio.learning_ui import LearningInterface, POSITIONS, number


def complete_cycle(demo: LearningDemo) -> None:
    """Run just the remaining stages of the present cycle."""
    while demo.stage != Stage.COMPARISON:
        demo.advance()


class LearningMathTests(unittest.TestCase):
    def test_all_twelve_gradients_match_independent_finite_differences(self) -> None:
        parameters = DemoParameters(np.array(((.6, -.3), (.2, .3))), np.array((.1, .1)),
                                    np.array(((.4, -.2), (-.3, .8))), np.array((-.2, .1)))
        inputs = np.array((.8, .2))
        for label in (0, 5):
            step = calculate_step(inputs, parameters, label)
            gradients = (step.gradients.hidden_weights, step.gradients.hidden_bias,
                         step.gradients.output_weights, step.gradients.output_bias)
            for block, values in enumerate(parameter_arrays(parameters)):
                for index in np.ndindex(values.shape):
                    plus = [array.copy() for array in parameter_arrays(parameters)]
                    minus = [array.copy() for array in parameter_arrays(parameters)]
                    plus[block][index] += 1e-6
                    minus[block][index] -= 1e-6
                    high = cross_entropy_scores(run_forward(inputs, DemoParameters(*plus)).scores, label)
                    low = cross_entropy_scores(run_forward(inputs, DemoParameters(*minus)).scores, label)
                    self.assertAlmostEqual(gradients[block][index], (high - low) / 2e-6, places=7)

    def test_relu_blocks_hidden_gradient_but_output_bias_still_learns(self) -> None:
        params = initialize_parameters(23)
        step = calculate_step(np.array((.625, .875)), params, 5)
        np.testing.assert_allclose(step.forward_before.scores, (-.64925, .0434625))
        np.testing.assert_array_equal(step.gradients.relu_slopes, (1, 0))
        np.testing.assert_array_equal(step.gradients.hidden_weights[1], (0, 0))
        np.testing.assert_array_equal(step.gradients.output_weights[:, 1], (0, 0))
        self.assertEqual(step.gradients.hidden_bias[1], 0)
        self.assertNotEqual(step.gradients.output_bias[1], 0)
        self.assertLess(step.loss_after, step.loss_before)

    def test_update_is_simultaneous_and_snapshots_do_not_alias(self) -> None:
        params = initialize_parameters()
        previous = [array.copy() for array in parameter_arrays(params)]
        step = calculate_step(np.array((.625, .875)), params, 5, .3)
        gradients = (step.gradients.hidden_weights, step.gradients.hidden_bias,
                     step.gradients.output_weights, step.gradients.output_bias)
        for old, current, gradient, new in zip(previous, parameter_arrays(params), gradients, parameter_arrays(step.after)):
            np.testing.assert_array_equal(old, current)
            np.testing.assert_allclose(new, old - .3 * gradient)
            self.assertFalse(new.flags.writeable)
        self.assertFalse(step.forward_before.probabilities.flags.writeable)
        self.assertFalse(step.gradients.score_deltas.flags.writeable)

    def test_cross_entropy_is_stable_when_correct_probability_underflows(self) -> None:
        self.assertEqual(cross_entropy_scores(np.array((1000., -1000.)), 5), 2000)
        self.assertAlmostEqual(cross_entropy_scores(np.array((1000., 999.)), 0), np.log1p(np.exp(-1)))
        with self.assertRaises(ValueError):
            target_vector(3)

    def test_invalid_rates_do_not_change_a_prepared_iteration(self) -> None:
        demo = LearningDemo(*examples())
        step = demo.step
        for rate in (0, -1, np.nan, np.inf):
            with self.assertRaisesRegex(ValueError, "positiva e finita"):
                demo.set_learning_rate(rate)
            self.assertIs(demo.step, step)
            self.assertEqual(demo.total_updates, 0)


class LearningNavigationTests(unittest.TestCase):
    def test_gradients_do_not_learn_and_rewind_never_applies_update_twice(self) -> None:
        demo = LearningDemo(*examples())
        original = demo.parameters
        for _ in range(7):
            demo.advance()
        self.assertIs(demo.parameters, original)
        self.assertEqual(demo.total_updates, 0)
        demo.advance()
        updated = demo.parameters
        self.assertEqual(demo.total_updates, 1)
        for _ in range(3):
            demo.go_back()
        for _ in range(5):
            demo.advance()
        self.assertIs(demo.parameters, updated)
        self.assertEqual(demo.total_updates, 1)
        self.assertEqual(len(demo.loss_history), 2)
        with self.assertRaisesRegex(ValueError, "fixada"):
            demo.set_learning_rate(.2)

    def test_next_cycle_uses_updated_parameters_and_can_alternate_samples(self) -> None:
        demo = LearningDemo(*examples())
        complete_cycle(demo)
        trained = demo.parameters
        previous_loss = demo.step.loss_after
        demo.next_iteration()
        self.assertAlmostEqual(demo.step.loss_before, previous_loss)
        for a, b in zip(parameter_arrays(trained), parameter_arrays(demo.step.before)):
            np.testing.assert_array_equal(a, b)
        complete_cycle(demo)
        demo.next_iteration(advance_example=True)
        self.assertEqual(demo.label, 0)
        self.assertEqual(demo.total_updates, 2)
        self.assertEqual(demo.history_updates, [0, 1, 2])

    def test_changing_digit_keeps_curve_but_changing_pixels_restarts_objective(self) -> None:
        demo = LearningDemo(*examples())
        complete_cycle(demo)
        trained, losses = demo.parameters, demo.loss_history.copy()
        demo.next_example()
        self.assertIs(demo.parameters, trained)
        self.assertEqual(demo.loss_history, losses)
        self.assertAlmostEqual(losses[-1], demo.mean_training_loss(trained))
        demo.select_pixel(0, 20)
        self.assertIs(demo.parameters, trained)
        self.assertEqual(demo.history_updates, [1])
        self.assertEqual(len(demo.loss_history), 1)
        with self.assertRaisesRegex(ValueError, "diferentes"):
            demo.select_pixel(0, demo.pixel_indices[1])

    def test_reset_restores_the_forward_exercise_initialization(self) -> None:
        demo = LearningDemo(*examples())
        complete_cycle(demo)
        demo.randomize()
        demo.reset()
        self.assertEqual(demo.stage, Stage.NETWORK)
        self.assertEqual(demo.total_updates, 0)
        self.assertEqual(demo.label, 5)
        for actual, expected in zip(parameter_arrays(demo.parameters), parameter_arrays(initialize_parameters(23))):
            np.testing.assert_array_equal(actual, expected)


class LearningCanvasTests(unittest.TestCase):
    def tearDown(self) -> None:
        plt.close("all")

    def test_hidden_chain_rule_displays_weights_and_zero_has_no_negative_sign(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            for _ in range(6):
                ui.advance()
        self.assertEqual(ui.demo.stage, Stage.HIDDEN_DELTA)
        self.assertIn("w =", ui._edge_text("output", 0, 0))
        self.assertEqual(number(-0.), "0")

    def test_real_buttons_and_neuron_clicks_reveal_the_selected_derivative(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            for _ in range(6):
                click(ui.figure, ui.buttons[1].ax, (.5, .5))
            click(ui.figure, ui.main_axis, POSITIONS["h2"])
        self.assertEqual(ui.demo.stage, Stage.HIDDEN_DELTA)
        self.assertEqual(ui.focus, ("hidden", 1))
        self.assertIn("H2:", ui.detail_axis.texts[0].get_text())
        self.assertEqual(ui.demo.total_updates, 0)

    def test_image_selection_and_slider_do_not_train_implicitly(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        click(ui.figure, ui.image_axis, (4, 2))
        self.assertEqual(ui.demo.pixel_indices, (20, 10))
        self.assertEqual(ui.input_slot, 1)
        ui.rate_slider.set_val(.3)
        self.assertAlmostEqual(ui.demo.learning_rate, .3)
        self.assertEqual(ui.demo.total_updates, 0)
        self.assertEqual(len(ui.demo.loss_history), 1)

    def test_animated_cycle_stops_with_one_update(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            ui.toggle_running()
            for _ in range(240):
                ui.tick()
        self.assertEqual(ui.demo.stage, Stage.COMPARISON)
        self.assertFalse(ui.is_running)
        self.assertEqual(ui.demo.total_updates, 1)
        self.assertFalse(ui.rate_slider.active)

    def test_training_repeats_all_phases_and_pause_does_not_learn(self) -> None:
        ui = LearningInterface(*examples(), animate=False, training_cycles=3)
        visited = set()
        with patch.object(ui.figure.canvas, "draw_idle"):
            ui.toggle_training()
            for _ in range(40):
                visited.add(ui.demo.stage)
                ui.tick()
            ui.toggle_training()
            paused = ui.demo.total_updates
            for _ in range(25):
                ui.tick()
            self.assertEqual(ui.demo.total_updates, paused)
            self.assertFalse(ui.is_running)
            ui.toggle_training()
            for _ in range(300):
                visited.add(ui.demo.stage)
                ui.tick()
        self.assertEqual(visited, set(Stage))
        self.assertEqual(ui.demo.total_updates, 3)
        self.assertEqual(ui.demo.history_updates, [0, 1, 2, 3])
        self.assertFalse(ui.is_running)
        self.assertIsNone(ui.training_goal)
        self.assertEqual(ui.demo.label, 5)

    def test_next_after_the_comparison_repeats_the_cycle_without_another_update(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            while ui.demo.stage != Stage.COMPARISON:
                ui.advance()
            ui.advance()
        self.assertEqual(ui.demo.stage, Stage.NETWORK)
        self.assertEqual(ui.demo.total_updates, 1)
        self.assertIn("Novo ciclo", ui.detail_axis.texts[0].get_text())

    def test_forward_animation_reaches_the_output_layer_after_the_hidden_layer(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            ui.advance()
            ui.is_running = True
            ui.render()
            windows = {(begin, finish) for *_, begin, finish in ui.flow_paths}
            ui._move_flow_dots(0.2)
            hidden_value = ui.node_texts["h1"].get_text()
            output_value = ui.node_texts["o0"].get_text()
        self.assertEqual(windows, {(0.0, .4), (.4, .8)})
        self.assertEqual(hidden_value, "H1")
        self.assertEqual(output_value, "s0")

    def test_weight_gradients_stop_on_their_weight_and_only_deltas_reach_a_node(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            ui.is_running = True
            for stage in (Stage.OUTPUT_PARAMETERS, Stage.HIDDEN_DELTA, Stage.HIDDEN_PARAMETERS):
                while ui.demo.stage != stage:
                    ui.demo.advance()
                ui.render()
                ends = [end for _, end, *_ in ui.flow_paths]
                self.assertTrue(ends, stage.name)
                # Backwards dots stop beside the hidden nodes (x = 6) only when δ is propagated;
                # weight gradients stop on the weight labels (x = 2,4 / 4,7 / 7,4 / 9,7).
                reaches_node = all(6 < end[0] < 6.6 for end in ends)
                self.assertEqual(reaches_node, stage == Stage.HIDDEN_DELTA, stage.name)
                self.assertFalse(any(end[0] < 1.6 for end in ends), "nada chega às entradas")
                ui._move_flow_dots(0.1)
                hidden = ui.node_texts["h1"].get_text()
                self.assertEqual(hidden == "δH1", stage == Stage.HIDDEN_DELTA, stage.name)

    def test_calculations_inside_nodes_pulse_without_moving_dots(self) -> None:
        ui = LearningInterface(*examples(), animate=False)
        with patch.object(ui.figure.canvas, "draw_idle"):
            ui.is_running = True
            for stage in (Stage.PROBABILITIES, Stage.LOSS, Stage.OUTPUT_DELTA, Stage.UPDATE):
                while ui.demo.stage != stage:
                    ui.demo.advance()
                ui.render()
                self.assertEqual(ui.flow_dots, [], stage.name)
                self.assertTrue(ui.pulses, stage.name)

    def test_headless_entry_finishes_without_window_or_terminal_pause(self) -> None:
        with patch.dict(os.environ, {"FORMACAO_ML_NO_PAUSE": "1"}), \
             patch.object(learning, "load_binary_demo_examples", return_value=examples()), \
             patch.object(plt, "show") as show:
            learning.main()
        show.assert_not_called()
        self.assertEqual(plt.get_fignums(), [])


class SharedDemoDataTests(unittest.TestCase):
    def test_selected_examples_come_only_from_training_and_keep_first_digit(self) -> None:
        images = np.zeros((70, 8, 8), dtype=np.float64)
        labels = np.zeros(70, dtype=np.int64)
        labels[[2, 4, 6, 65]] = 5
        images[65] = 12
        reserved = np.full((2, 8, 8), 16., dtype=np.float64)
        with patch.object(digit_dataset, "load_digit_splits", return_value=(images, labels, reserved, np.array([0, 5]))):
            selected, targets = digit_dataset.load_binary_demo_examples()
        np.testing.assert_array_equal(targets, (5, 0, 5, 0, 5, 0))
        np.testing.assert_array_equal(selected[0], images[65])
        self.assertFalse(np.any(selected == 16))


if __name__ == "__main__":
    unittest.main()
