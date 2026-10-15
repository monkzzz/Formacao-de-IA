"""Numerical, split, update and actual-canvas contracts for exercises04 and05."""
from __future__ import annotations
import unittest
from unittest.mock import patch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.backend_bases import MouseEvent
from tests.test_ml_exercises import mlp
from apoio.evaluation_metrics import binary_metrics, metric_scenarios, roc_curve
from apoio.metrics_ui import MetricsInterface, TITLES
from apoio.digit_training_demo import DigitTrainingDemo
from apoio.digit_training_ui import DigitTrainingInterface


def synthetic_splits():
    """Distinct official-like splits, with enough class coverage for validation."""
    random = np.random.default_rng(81)
    # UCI intensities are integer counts0..16. This also makes the round trip
    # through repeated drawing cells exact, rather than subject to float sums.
    return (random.integers(0,17,(80,8,8)).astype(float), np.repeat(np.arange(10),8),
            random.integers(0,17,(20,8,8)).astype(float), np.repeat(np.arange(10),2))


def session() -> DigitTrainingDemo:
    """Use only an in-memory dataset, preserving the production split code."""
    with patch.object(mlp, "load_digit_splits", side_effect=synthetic_splits):
        return DigitTrainingDemo(mlp)


def click(figure, axis, point) -> None:
    """Dispatch the same canvas mouse events used by the real controls."""
    figure.canvas.draw()
    x,y = axis.transData.transform(point)
    for name in ("button_press_event", "button_release_event"):
        figure.canvas.callbacks.process(name, MouseEvent(name,figure.canvas,x,y,button=1))


class EvaluationTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_counts_and_thresholds_match_slides(self):
        large,small,rare = metric_scenarios()
        m = binary_metrics(large.labels,(large.scores >= .5).astype(int))
        self.assertEqual((m.true_positives,m.false_negatives,m.false_positives,m.true_negatives),(16,4,8,72))
        self.assertAlmostEqual(m.f1,32/44)
        high = binary_metrics(small.labels,(small.scores >= .7).astype(int))
        low = binary_metrics(small.labels,(small.scores >= .3).astype(int))
        self.assertEqual((high.precision,high.recall),(1,.5))
        self.assertAlmostEqual(low.precision,4/7)
        self.assertEqual(low.recall,1)
        baseline = binary_metrics(rare.labels,np.zeros(100,dtype=int))
        self.assertEqual((baseline.accuracy,baseline.recall),(.98,0))

    def test_auc_including_ties_and_invalid_inputs(self):
        small = metric_scenarios()[1]
        self.assertEqual(roc_curve(small.labels,small.scores)[2],.75)
        self.assertEqual(roc_curve(np.array([0,1]),np.array([.5,.5]))[2],.5)
        for labels,scores in ((np.array([]),np.array([])),(np.array([0,2]),np.array([.1,.9])),
                              (np.array([0,1]),np.array([.1,np.nan]))):
            with self.assertRaises(ValueError):
                roc_curve(labels,scores)

    def test_actual_confusion_click_traces_exact_samples(self):
        ui = MetricsInterface()
        ui.advance();ui.advance()
        click(ui.figure,ui.result_axis,(1,0))
        self.assertEqual(ui.group,"FN")
        self.assertEqual(np.count_nonzero(ui._groups() == ui.group),4)
        original = ui.scenario.scores.copy()
        ui.slider.set_val(.1)
        np.testing.assert_array_equal(ui.scenario.scores,original)
        self.assertIsNone(ui.group)
        self.assertEqual(ui.metrics.recall,1)

    def test_baseline_scenario_and_playback_stop(self):
        ui = MetricsInterface()
        ui.next_scenario();ui.next_scenario();ui.baseline()
        self.assertEqual(ui.metrics.accuracy,.98)
        self.assertEqual(ui.metrics.recall,0)
        ui.animate()
        for _ in range(len(TITLES) - 1):ui.tick()
        self.assertFalse(ui.is_running)
        self.assertEqual(ui.stage,len(TITLES) - 1)
        ui.reset()
        self.assertEqual((ui.stage,ui.scenario_index,ui.threshold),(0,0,.5))

    def test_metric_pages_trace_the_correct_reference_population(self):
        ui = MetricsInterface()
        # The same decisions give 24 alarms but 20 real defects. Visually
        # mixing these two populations teaches the wrong denominator.
        for stage, visible, result in ((3,100,"88,0%"), (4,24,"66,7%"),
                                       (5,20,"80,0%"), (6,28,"72,7%")):
            ui.stage = stage
            ui.render()
            self.assertEqual(sum(dot.get_alpha() == 1 for dot in ui.samples_axis.collections),visible)
            self.assertIn(result,[text.get_text() for text in ui.result_axis.texts])
        original = ui.scenario.scores.copy()
        ui.next_scenario()
        ui.stage = 4
        ui.slider.set_val(.7)
        self.assertIn("100,0%",[text.get_text() for text in ui.result_axis.texts])
        ui.stage = 5
        ui.render()
        self.assertIn("50,0%",[text.get_text() for text in ui.result_axis.texts])
        np.testing.assert_array_equal(ui.scenarios[0].scores,original)

    def test_no_alarms_explains_undefined_precision_instead_of_false_certainty(self):
        ui = MetricsInterface()
        ui.stage = 4
        ui.baseline()
        content = " ".join(text.get_text() for text in ui.result_axis.texts)
        self.assertIn("não está definida",content)
        self.assertIn("0 por convenção",content)
        self.assertIn("0,0%",content)
        ui.stage = len(TITLES) - 1
        ui.render()
        ui.previous()
        ui.render()
        self.assertIn("Custo total:"," ".join(t.get_text() for t in ui.result_axis.texts))


class DigitTrainingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def tearDown(self):
        plt.close("all")

    def test_training_never_measures_test_and_inspection_uses_validation(self):
        d = session()
        self.assertFalse(set(d.train_indices)&set(d.validation_indices))
        np.testing.assert_array_equal(d.validation_image,d.images[d.validation_indices[0]])
        with patch.object(mlp,"to_feature_tensor",wraps=mlp.to_feature_tensor) as convert:
            d.train_epoch();d.inspect(d.validation_image)
        self.assertFalse(any(call.args[0] is d.test_images for call in convert.call_args_list))
        self.assertIsNone(d.test_result)

    def test_gradients_do_not_update_and_sgd_updates_all_parameters(self):
        d = session()
        old = [p.detach().clone() for p in d.model.parameters()]
        for _ in range(3):d.advance_phase()
        for before,p in zip(old,d.model.parameters()):
            torch.testing.assert_close(before,p)
        gradients = [p.grad.detach().clone() for p in d.model.parameters()]
        d.advance_phase()
        for before,p,g in zip(old,d.model.parameters(),gradients):
            torch.testing.assert_close(p,before-.1*g)
        self.assertEqual((d.updates,d.epoch,d.phase),(1,1,0))
        np.testing.assert_allclose(d.last_delta.numpy(),-.1*d.last_gradient.numpy(),atol=1e-8)

    def test_partial_batch_can_be_completed_by_epoch_training(self):
        d = session()
        d.advance_phase();d.advance_phase()
        d.train_epoch()
        self.assertEqual((d.updates,d.epoch,d.phase),(1,1,0))
        self.assertEqual(len(d.history),2)

    def test_freeze_loads_validation_checkpoint_and_caches_test(self):
        d = session()
        d.train_epoch()
        # Simulate a later epoch degrading validation. The chosen snapshot must
        # still supply the final model, rather than the current training weights.
        selected = {k:v.clone() for k,v in d.best_state.items()}
        with torch.no_grad():
            d.model.output_layer.bias.add_(5)
        with patch.object(mlp,"to_feature_tensor",wraps=mlp.to_feature_tensor) as convert:
            first = d.evaluate_test()
            second = d.evaluate_test()
        self.assertIs(first,second)
        self.assertEqual(sum(call.args[0] is d.test_images for call in convert.call_args_list),1)
        for key,p in d.final_model.state_dict().items():
            torch.testing.assert_close(p,selected[key])
        with self.assertRaises(RuntimeError):d.advance_phase()
        with self.assertRaises(RuntimeError):d.train_epoch()

    def test_test_rejects_untrained_or_partial_epoch(self):
        d = session()
        with self.assertRaises(RuntimeError):d.evaluate_test()
        d.train_epoch();d.advance_phase()
        with self.assertRaises(RuntimeError):d.evaluate_test()
        self.assertIsNone(d.test_result)

    def test_reset_is_deterministic_and_clears_test(self):
        d = session()
        d.train_epoch()
        first = {k:v.clone() for k,v in d.model.state_dict().items()}
        d.evaluate_test();d.reset();d.train_epoch()
        for key,p in d.model.state_dict().items():
            torch.testing.assert_close(p,first[key],rtol=0,atol=0)
        self.assertIsNone(d.test_result)
        self.assertFalse(d.is_frozen)

    def test_gui_rewinding_never_repeats_optimizer_step(self):
        ui = DigitTrainingInterface(session())
        for _ in range(7):ui.advance()
        self.assertEqual(ui.demo.updates,1)
        for _ in range(5):ui.previous()
        for _ in range(5):ui.advance()
        self.assertEqual(ui.demo.updates,1)

    def test_next_batch_repeats_the_cycle_step_by_step(self):
        with patch.object(mlp,"BATCH_SIZE",16):
            ui = DigitTrainingInterface(session())
            for _ in range(7):ui.advance()
            first = ui.demo.batch_indices.clone()
            ui.next_batch()
            self.assertEqual((ui.stage,ui.demo.phase,ui.demo.updates),(3,1,1))
            self.assertFalse(torch.equal(first,ui.demo.batch_indices))
            for stage in (4,5,6,7):
                ui.advance();self.assertEqual(ui.stage,stage)
            self.assertEqual(ui.demo.updates,2)
            self.assertEqual(len(ui.demo.batch_history),2)
            # The loss page shows every image of the batch; their mean is the batch loss.
            self.assertAlmostEqual(float(ui.demo.sample_losses.mean()),ui.demo.last_loss,places=5)
            ui.advance()
            self.assertEqual(ui.stage,7)
            self.assertIn("pelo menos uma época",ui.notice)
            ui.demo.train_epoch();ui.next_batch()
            for _ in range(4):ui.advance()
            ui.advance()
            self.assertIn("está a meio",ui.notice)

    def test_next_batch_completes_a_half_shown_batch_first(self):
        ui = DigitTrainingInterface(session())
        for _ in range(4):ui.advance()
        ui.next_batch()
        self.assertEqual((ui.stage,ui.demo.phase,ui.demo.updates),(3,1,1))
        self.assertIn("concluído",ui.notice)

    def test_training_timer_pause_resume_and_freeze_controls(self):
        ui = DigitTrainingInterface(session())
        ui.train();ui.tick();ui.train()
        self.assertFalse(ui.is_running)
        self.assertEqual(ui.demo.epoch,1)
        ui.tick();self.assertEqual(ui.demo.epoch,1)
        ui.train()
        while ui.is_running:ui.tick()
        self.assertEqual(ui.demo.epoch,12)
        ui.evaluate()
        old = [p.detach().clone() for p in ui.demo.final_model.parameters()]
        ui.train();ui.next_batch()
        self.assertFalse(ui.is_running)
        for before,p in zip(old,ui.demo.final_model.parameters()):torch.testing.assert_close(before,p)

    def test_actual_drawing_is_pooled_and_inference_preserves_model(self):
        ui = DigitTrainingInterface(session())
        ui.demo.train_epoch();ui.evaluate();ui.use()
        old = [p.detach().clone() for p in ui.demo.final_model.parameters()]
        click(ui.figure,ui.image_axis,(10,6))
        click(ui.figure,ui.infer_button.ax,(.5,.5))
        self.assertGreater(float(ui.drawing.max()),0)
        self.assertAlmostEqual(float(ui.draw_probabilities.sum()),1,places=6)
        for before,p in zip(old,ui.demo.final_model.parameters()):torch.testing.assert_close(before,p)
        click(ui.figure,ui.clear_button.ax,(.5,.5))
        self.assertFalse(ui.drawing.any())
        self.assertIsNone(ui.draw_probabilities)

    def test_actual_multiclass_cell_selects_matching_test_images(self):
        ui = DigitTrainingInterface(session())
        ui.demo.train_epoch();ui.evaluate()
        confusion = ui.demo.test_result[0]
        real,predicted = np.argwhere(confusion > 0)[0]
        click(ui.figure,ui.main_axis,(predicted,real))
        indices = ui.selected_test_indices
        self.assertEqual(len(indices),confusion[real,predicted])
        self.assertTrue((ui.demo.test_labels[indices] == real).all())
        self.assertTrue((ui.demo.test_predictions[indices] == predicted).all())

    def test_validation_canvas_example_preserves_input_and_model(self):
        ui = DigitTrainingInterface(session())
        ui.demo.train_epoch();ui.evaluate();ui.use();ui.next_image()
        np.testing.assert_array_equal(mlp.downsample_drawing(ui.drawing),ui.demo.validation_image)
        ui.infer()
        np.testing.assert_allclose(ui.draw_probabilities,ui.demo.inspect(ui.demo.validation_image)[1])


if __name__ == "__main__":
    unittest.main()
