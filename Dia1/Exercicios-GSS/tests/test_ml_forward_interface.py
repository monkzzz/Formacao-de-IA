"""Numerical and real-canvas checks for the staged forward-pass GUI."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
import numpy as np

from tests.test_ml_core_exercises import forward_pass
from apoio.forward_pass_demo import DemoParameters, ForwardDemo, Stage, flatten_image, initialize_parameters, run_forward
from apoio.forward_pass_ui import ForwardPassInterface, POSITIONS


def examples():
    """Return controlled intensities with different first two selected pixels."""
    first = np.arange(64, dtype=np.float64).reshape(8, 8) % 17
    return np.stack((first, np.flipud(first))), np.array((5, 0), dtype=np.int64)


def click(figure, axis, point) -> None:
    """Exercise the registered callbacks through actual canvas coordinates."""
    figure.canvas.draw()
    x, y = axis.transData.transform(point)
    for name in ("button_press_event", "button_release_event"):
        event = MouseEvent(name, figure.canvas, x, y, button=1)
        figure.canvas.callbacks.process(name, event)


class SmallNetworkTests(unittest.TestCase):
    def test_two_neurons_and_softmax_match_a_hand_worked_example(self) -> None:
        parameters = DemoParameters(np.array(((.6, -.3), (-.5, .2))), np.array((.1, .1)),
                                    np.array(((.4, -.2), (-.3, .8))), np.array((-.2, .1)))
        result = run_forward(np.array((.8, .2)), parameters)
        np.testing.assert_allclose(result.hidden_contributions, ((.48, -.06), (-.4, .04)))
        np.testing.assert_allclose(result.hidden_sums, (.52, -.26))
        np.testing.assert_allclose(result.hidden_activations, (.52, 0))
        np.testing.assert_allclose(result.scores, (.008, -.056))
        self.assertAlmostEqual(result.probabilities[0], 1 / (1 + np.exp(-.064)))

    def test_large_scores_are_stable_and_parameters_never_change(self) -> None:
        parameters = initialize_parameters()
        previous = parameters.hidden_weights.copy()
        high_scores = DemoParameters(parameters.hidden_weights, parameters.hidden_bias,
                                    parameters.output_weights, np.array((1000., 999.)))
        result = run_forward(np.array((.25, .75)), high_scores)
        self.assertTrue(np.isfinite(result.probabilities).all())
        self.assertAlmostEqual(result.probabilities.sum(), 1)
        np.testing.assert_array_equal(parameters.hidden_weights, previous)
        self.assertFalse(parameters.hidden_weights.flags.writeable)

    def test_initialization_includes_biases_and_is_reproducible(self) -> None:
        a, b = initialize_parameters(23), initialize_parameters(23)
        np.testing.assert_array_equal(a.hidden_weights, b.hidden_weights)
        np.testing.assert_array_equal(a.output_bias, b.output_bias)
        self.assertGreater(np.abs(a.hidden_bias).sum(), 0)
        self.assertGreater(np.abs(a.output_bias).sum(), 0)

    def test_flatten_mapping_and_input_boundaries(self) -> None:
        image = examples()[0][0]
        vector = flatten_image(image)
        self.assertEqual(vector.shape, (64,))
        self.assertEqual(vector[10], image[1, 2] / 16)
        for invalid in (np.zeros((7, 8)), np.full((8, 8), np.nan), np.full((8, 8), 17)):
            with self.assertRaises(ValueError):
                flatten_image(invalid)
        with self.assertRaises(ValueError):
            run_forward(np.array((1.,)), initialize_parameters())


class DemoNavigationTests(unittest.TestCase):
    def test_parameters_and_result_are_initialized_only_at_their_stages(self) -> None:
        demo = ForwardDemo(*examples())
        for _ in range(3):
            demo.advance()
        self.assertIsNone(demo.parameters)
        demo.advance()
        self.assertIsNotNone(demo.parameters)
        self.assertIsNone(demo.result)
        demo.advance()
        self.assertIsNotNone(demo.result)
        original = demo.parameters
        demo.go_back()
        demo.advance()
        self.assertIs(demo.parameters, original)

    def test_new_pixel_and_digit_invalidate_pass_but_keep_the_same_network(self) -> None:
        demo = ForwardDemo(*examples())
        for _ in range(9):
            demo.advance()
        parameters = demo.parameters
        demo.select_pixel(0, 20)
        self.assertIsNone(demo.result)
        self.assertEqual(demo.inputs[0], demo.image[2, 4] / 16)
        self.assertIs(demo.parameters, parameters)
        demo.next_example()
        self.assertIsNone(demo.result)
        self.assertIs(demo.parameters, parameters)
        self.assertEqual(demo.stage, Stage.IMAGE)

    def test_duplicate_pixel_is_rejected_and_reset_restores_seed(self) -> None:
        demo = ForwardDemo(*examples())
        with self.assertRaisesRegex(ValueError, "diferentes"):
            demo.select_pixel(0, 10)
        demo.randomize()
        changed = demo.parameters.hidden_weights.copy()
        demo.reset()
        for _ in range(4):
            demo.advance()
        self.assertFalse(np.array_equal(changed, demo.parameters.hidden_weights))
        np.testing.assert_array_equal(demo.parameters.hidden_weights, initialize_parameters(23).hidden_weights)


class ForwardCanvasTests(unittest.TestCase):
    def tearDown(self) -> None:
        plt.close("all")

    def test_buttons_advance_and_pixel_clicks_use_row_major_mapping(self) -> None:
        ui = ForwardPassInterface(*examples(), animate=False)
        for _ in range(2):
            click(ui.figure, ui.buttons[1].ax, (.5, .5))
        self.assertEqual(ui.demo.stage, Stage.FLATTEN)
        click(ui.figure, ui.image_axis, (4, 2))
        self.assertEqual(ui.demo.pixel_indices, (20, 10))
        self.assertEqual(ui.input_slot, 1)
        click(ui.figure, ui.main_axis, (30, 1.5))
        self.assertEqual(ui.demo.pixel_indices, (20, 30))

    def test_each_parameterized_neuron_is_inspectable_before_the_pass(self) -> None:
        ui = ForwardPassInterface(*examples(), animate=False)
        for _ in range(4):
            ui.advance()
        click(ui.figure, ui.main_axis, POSITIONS["o5"])
        self.assertEqual(ui.focus, ("output", 1))
        self.assertIsNone(ui.demo.result)
        self.assertIn("h1 ×", " ".join(t.get_text() for t in ui.detail_axis.texts))

    def test_manual_playback_stops_at_the_result_without_learning(self) -> None:
        ui = ForwardPassInterface(*examples(), animate=False)
        ui.toggle_running()
        for _ in range(180):
            ui.tick()
        self.assertEqual(ui.demo.stage, Stage.RESULT)
        self.assertFalse(ui.is_running)
        expected = initialize_parameters(23)
        np.testing.assert_array_equal(ui.demo.parameters.hidden_weights, expected.hidden_weights)
        np.testing.assert_array_equal(ui.demo.parameters.output_bias, expected.output_bias)
        self.assertIn("sem treino", ui.status.get_text())

    def test_previous_and_randomize_do_not_reveal_stale_output(self) -> None:
        ui = ForwardPassInterface(*examples(), animate=False)
        for _ in range(8):
            ui.advance()
        ui.previous()
        ui.previous()
        self.assertEqual(ui.focus, ("hidden", 1))
        ui.randomize()
        self.assertEqual(ui.demo.stage, Stage.PARAMETERS)
        self.assertIsNone(ui.demo.result)
        self.assertNotIn("Soma =", " ".join(t.get_text() for t in ui.detail_axis.texts))

    def test_headless_entry_does_not_open_or_wait(self) -> None:
        with patch.dict(os.environ, {"FORMACAO_ML_NO_PAUSE": "1"}), \
             patch.object(forward_pass, "load_demo_examples", return_value=examples()), \
             patch.object(plt, "show") as show:
            forward_pass.main()
        show.assert_not_called()
        self.assertEqual(plt.get_fignums(), [])


if __name__ == "__main__":
    unittest.main()
