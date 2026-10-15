"""Unit tests for the reusable logic in the machine-learning exercises."""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent

ROOT = Path(__file__).resolve().parents[1]
EXERCISE_DIRECTORY = ROOT / "modulo1"
sys.path.insert(0, str(EXERCISE_DIRECTORY))

from apoio import dataset_cache


def load_exercise_module(file_name: str, module_name: str):
    """Import an exercise whose filename starts with a numeric lesson number."""
    spec = importlib.util.spec_from_file_location(
        module_name,
        EXERCISE_DIRECTORY / file_name,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao foi possivel carregar {file_name}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


mlp = load_exercise_module(
    "dia1_modulo1_05_mlp_digitos.py",
    "digit_mlp",
)


class DatasetCacheTests(unittest.TestCase):
    def test_cache_remains_at_repository_root_after_module_move(self) -> None:
        self.assertEqual(dataset_cache.CACHE_DIRECTORY, ROOT / ".cache" / "datasets")

    def test_download_is_cached_for_later_calls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(dataset_cache, "CACHE_DIRECTORY", Path(directory)),
                patch.object(dataset_cache, "urlopen", return_value=io.BytesIO(b"zip")) as opener,
            ):
                first = dataset_cache.load_dataset_archive("https://example.test/data", "data.zip", "test")
                second = dataset_cache.load_dataset_archive("https://example.test/data", "data.zip", "test")

        self.assertEqual(first, b"zip")
        self.assertEqual(second, b"zip")
        opener.assert_called_once()

    def test_offline_download_error_explains_how_to_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(dataset_cache, "CACHE_DIRECTORY", Path(directory)),
                patch.object(dataset_cache, "urlopen", side_effect=URLError("offline")),
                self.assertRaisesRegex(RuntimeError, "verifica a ligacao a internet"),
            ):
                dataset_cache.load_dataset_archive(
                    "https://example.test/data",
                    "data.zip",
                    "test",
                )


class ExerciseLogicTests(unittest.TestCase):
    def test_digit_mlp_split_is_stratified_and_disjoint(self) -> None:
        labels = np.repeat(np.arange(10, dtype=np.int64), 8)
        training, validation = mlp.stratified_train_validation_split(
            labels,
            validation_fraction=0.25,
            seed=9,
        )

        self.assertEqual(set(training) & set(validation), set())
        self.assertEqual(sorted(np.concatenate((training, validation))), list(range(80)))
        np.testing.assert_array_equal(
            np.bincount(labels[training], minlength=10),
            np.full(10, 6),
        )
        np.testing.assert_array_equal(
            np.bincount(labels[validation], minlength=10),
            np.full(10, 2),
        )

    def test_digit_mlp_training_returns_finite_metrics(self) -> None:
        labels = np.repeat(np.arange(10, dtype=np.int64), 4)
        random = np.random.default_rng(7)
        images = random.uniform(0.0, 16.0, size=(40, 8, 8))
        training_indices, validation_indices = mlp.stratified_train_validation_split(
            labels,
            validation_fraction=0.25,
        )
        model, history = mlp.train_model(
            mlp.to_feature_tensor(images[training_indices]),
            mlp.to_label_tensor(labels[training_indices]),
            mlp.to_feature_tensor(images[validation_indices]),
            mlp.to_label_tensor(labels[validation_indices]),
            epochs=1,
            batch_size=16,
        )

        self.assertEqual(len(history), 1)
        self.assertTrue(np.isfinite(history[0].train_loss))
        self.assertTrue(np.isfinite(history[0].validation_loss))
        self.assertEqual(model(mlp.to_feature_tensor(images[:2])).shape, (2, 10))

    def test_digit_mlp_multiclass_metrics_match_confusion_matrix(self) -> None:
        expected = np.array((0, 0, 1, 1, 2), dtype=np.int64)
        predicted = np.array((0, 1, 1, 2, 2), dtype=np.int64)

        confusion, accuracy, precision, recall, f1 = mlp.summarize_classification(
            expected,
            predicted,
            class_count=3,
        )

        np.testing.assert_array_equal(
            confusion,
            np.array(((1, 1, 0), (0, 1, 1), (0, 0, 1))),
        )
        self.assertAlmostEqual(accuracy, 0.6)
        self.assertAlmostEqual(precision, (1.0 + 0.5 + 0.5) / 3)
        self.assertAlmostEqual(recall, (0.5 + 0.5 + 1.0) / 3)
        self.assertAlmostEqual(f1, (2 / 3 + 0.5 + 2 / 3) / 3)

    def test_digit_mlp_multiclass_metrics_reject_misaligned_labels(self) -> None:
        with self.assertRaisesRegex(ValueError, "vetores nao vazios iguais"):
            mlp.summarize_classification(
                np.array((0, 1)),
                np.array((0,)),
            )

    def test_digit_drawing_is_pooled_to_the_model_input(self) -> None:
        drawing = np.zeros((mlp.DRAWING_SIZE, mlp.DRAWING_SIZE))
        mlp.draw_segment(drawing, (6, 4), (8, 4), brush_radius=0.5)

        image = mlp.downsample_drawing(drawing)

        self.assertEqual(image.shape, (8, 8))
        self.assertAlmostEqual(image[1, 2], 16.0 / 3.0)
        self.assertGreater(np.count_nonzero(image), 0)

    def test_digit_drawing_inference_returns_probabilities(self) -> None:
        model = mlp.DigitMLP()
        image = np.zeros((8, 8), dtype=np.float64)
        image[2:6, 3:5] = 16.0

        digit, probabilities = mlp.predict_drawn_digit(model, image)

        self.assertIn(digit, range(10))
        self.assertEqual(probabilities.shape, (10,))
        self.assertAlmostEqual(float(probabilities.sum()), 1.0, places=6)

    def test_drawing_window_mouse_stroke_reaches_model_inference(self) -> None:
        model = mlp.DigitMLP()
        with patch.object(
            mlp,
            "predict_drawn_digit",
            wraps=mlp.predict_drawn_digit,
        ) as predict:
            def draw_and_infer() -> None:
                figure = plt.gcf()
                canvas = figure.canvas
                canvas.draw()
                drawing_axis, _, infer_axis, _ = figure.axes

                def send_mouse_event(
                    name: str,
                    axis: plt.Axes,
                    point: tuple[float, float],
                ) -> None:
                    x, y = axis.transData.transform(point)
                    event = MouseEvent(
                        name,
                        canvas,
                        x,
                        y,
                        button=1,
                    )
                    canvas.callbacks.process(name, event)

                send_mouse_event("button_press_event", drawing_axis, (6, 4))
                send_mouse_event("motion_notify_event", drawing_axis, (8, 4))
                send_mouse_event("button_release_event", drawing_axis, (8, 4))
                send_mouse_event("button_press_event", infer_axis, (0.5, 0.5))
                send_mouse_event("button_release_event", infer_axis, (0.5, 0.5))

            try:
                with patch.object(plt, "show", side_effect=draw_and_infer):
                    mlp.show_drawing_inference(model)
            finally:
                plt.close("all")

        predict.assert_called_once()
        drawn_image = predict.call_args.args[1]
        self.assertEqual(drawn_image.shape, (8, 8))
        self.assertGreater(float(drawn_image.max()), 0.0)


if __name__ == "__main__":
    unittest.main()
