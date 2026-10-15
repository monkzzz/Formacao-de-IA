"""Tests for the module 2 exercises (no network: recordings and mocks only)."""

from __future__ import annotations

import importlib.util
import math
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent

EXERCISE_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "modulo2"
)
sys.path.insert(0, str(EXERCISE_DIRECTORY))


def load_exercise(file_name: str, module_name: str):
    """Load an exercise module whose filename starts with a number."""
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


tokens_exercise = load_exercise("dia1_modulo2_01_tokens_ids.py", "language_tokens")
embedding_exercise = load_exercise("dia1_modulo2_02_mapa_embeddings.py", "language_embeddings")
attention = load_exercise("dia1_modulo2_03_attention.py", "language_attention")
next_token = load_exercise("dia1_modulo2_04_proximo_token.py", "language_next_token")
prompt_lab = load_exercise("dia1_modulo2_05_laboratorio_prompts.py", "language_prompt_lab")
vision_exercise = load_exercise("dia1_modulo2_06_imagem_texto.py", "language_vision")
from apoio_linguagem import lm_studio  # noqa: E402  (needs EXERCISE_DIRECTORY on sys.path)
from apoio_linguagem import imagem_texto as vision  # noqa: E402
from apoio_linguagem import laboratorio_prompts as laboratory  # noqa: E402
from apoio_linguagem import mapa_embeddings as embeddings  # noqa: E402
from apoio_linguagem import proximo_token  # noqa: E402
from apoio_linguagem import tokenizador_didatico as tokenizer  # noqa: E402


class TokenizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vocabulary = tokenizer.load_vocabulary()

    def test_slide_sentence_gives_the_slide_tokens_and_ids(self) -> None:
        # Contract with slide «Tokens e IDs»: same pieces and IDs, in the same order.
        tokens = tokenizer.tokenize("A peça parou e a peça partiu.", self.vocabulary)
        self.assertEqual(
            [(token.piece, token.token_id) for token in tokens],
            [("A", 37), ("pe", 905), ("##ça", 2210), ("par", 518), ("##ou", 77), ("e", 9), ("a", 12),
             ("pe", 905), ("##ça", 2210), ("par", 518), ("##tiu", 3120), (".", 4)],
        )

    def test_longest_pieces_first_and_unknown_words(self) -> None:
        pieces = [token.piece for token in tokenizer.tokenize("A linha 2 parou às 10h15.", self.vocabulary)]
        self.assertEqual(pieces, ["A", "linha", "2", "par", "##ou", "às", "10", "##h", "##15", "."])
        unknown = tokenizer.tokenize("Rolamento sobreaquecido!", self.vocabulary)
        self.assertEqual([token.piece for token in unknown], ["[UNK]", "[UNK]", "!"])

    def test_count_tokens_removes_the_chat_format(self) -> None:
        def fake_chat(messages, model, **options):
            text = messages[0]["content"]
            return {"usage": {"prompt_tokens": 66 + (1 if text == "." else 10)}}

        with patch.object(lm_studio, "request_chat", side_effect=fake_chat):
            self.assertEqual(lm_studio.count_tokens("A peça parou e a peça partiu."), 10)

    def test_interface_reports_repeated_pieces_and_recorded_count(self) -> None:
        interface = tokens_exercise.TokenInterface(self.vocabulary, live_counts=False)
        try:
            interface.choose_example(tokens_exercise.EXAMPLES[0][1])
            self.assertIn("pe (905) ×2", interface.summary.get_text())
            interface.count_in_model()
            self.assertIn("AMALIA: 10 tokens (gravado)", interface.model_line.get_text())
        finally:
            plt.close(interface.figure)


class EmbeddingMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = embeddings.RecordedEmbeddingSource()

    def test_recorded_vectors_group_most_phrases_by_area(self) -> None:
        texts = embeddings.all_base_texts()
        vectors = self.source.vectors(texts)
        np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1.0)
        # bge-m3 put 13 of 16 nearest neighbours in the same area; the slide relies on this.
        self.assertGreaterEqual(embeddings.same_area_rate(texts, vectors), 0.75)

    def test_bank_sentences_follow_their_context(self) -> None:
        sentences = self.source.vectors(list(embeddings.BANK_SENTENCES))
        anchors = self.source.vectors(list(embeddings.BANK_ANCHORS))
        similarity = sentences @ anchors.T
        self.assertGreater(similarity[0, 0], similarity[0, 1])  # money sentence → money phrase
        self.assertGreater(similarity[1, 1], similarity[1, 0])  # garden sentence → garden phrase

    def test_projection_needs_one_area_per_vector(self) -> None:
        vectors = self.source.vectors(embeddings.all_base_texts())
        with self.assertRaisesRegex(ValueError, "uma área"):
            embeddings.Projection(vectors, ["Manutenção"])

    def test_interface_adds_a_recorded_suggestion_and_lists_neighbours(self) -> None:
        interface = embedding_exercise.EmbeddingMapInterface(self.source)
        try:
            interface.add_suggestion()
            self.assertEqual(interface.added, [embeddings.SUGGESTIONS[0]])
            self.assertIn("Manutenção", interface.panel.get_text())
            interface.add_phrase("Frase que não foi gravada")
            self.assertIn("Sem vetor gravado", interface.status.get_text())
            interface.toggle_bank()
            self.assertIn("Modo «banco»", interface.panel.get_text())
        finally:
            plt.close(interface.figure)


class AttentionTests(unittest.TestCase):
    def test_query_a_uses_the_slide_weights(self) -> None:
        weights = attention.attention_weights(attention.QUERY_A, causal=True)
        np.testing.assert_allclose(weights[:10], (0.04, 0.52, 0.03, 0.14, 0.01, 0.02, 0.03, 0.12, 0.01, 0.08))
        self.assertTrue(np.all(weights[10:] == 0))

    def test_rows_sum_to_one_and_the_mask_blocks_the_future(self) -> None:
        causal = attention.attention_matrix(causal=True)
        free = attention.attention_matrix(causal=False)
        np.testing.assert_allclose(causal.sum(axis=1), 1.0)
        np.testing.assert_allclose(free.sum(axis=1), 1.0)
        self.assertTrue(np.all(np.triu(causal, k=1) == 0))
        self.assertGreater(free[attention.QUERY_A, attention.TOKENS.index("caixa")], 0)

    def test_clicking_a_word_selects_it(self) -> None:
        interface = attention.AttentionInterface()
        try:
            interface.figure.canvas.draw()
            x, y = interface.sentence_axis.transData.transform((interface.centres[3], 0.1))
            interface.on_click(MouseEvent("button_press_event", interface.figure.canvas, x, y, button=1))
            self.assertEqual(interface.query, 3)
            interface.toggle_mask()
            self.assertIn("desligada", interface.explanation.get_text())
        finally:
            plt.close(interface.figure)

    def test_matrix_is_hidden_until_requested(self) -> None:
        interface = attention.AttentionInterface()
        try:
            self.assertFalse(interface.matrix_axis.get_visible())
            interface.toggle_matrix()
            self.assertTrue(interface.matrix_axis.get_visible())
            self.assertEqual(interface.buttons[4].label.get_text(), "Esconder matriz")
        finally:
            plt.close(interface.figure)


class PromptLabTests(unittest.TestCase):
    def test_prompt_includes_the_selected_examples_and_rule(self) -> None:
        setup = laboratory.PromptSetup("Classificar", "ambíguo", 3, True)
        prompt = laboratory.build_prompt(setup)
        self.assertIn("dano físico da peça tem prioridade", prompt)
        self.assertEqual(prompt.count(": Manutenção") + prompt.count(": Qualidade") + prompt.count(": Logística"), 3)
        self.assertNotIn("Exemplos", laboratory.build_prompt(laboratory.PromptSetup(examples=0)))
        self.assertIn("Qualidade", laboratory.reference_for(setup))

    def test_recording_covers_every_button_combination(self) -> None:
        recorded = laboratory.RecordedPromptRunner()
        for setup in laboratory.all_setups():
            for temperature in laboratory.TEMPERATURES:
                for max_tokens in laboratory.MAX_TOKENS:
                    for repetition in range(laboratory.REPETITIONS):
                        key = laboratory.recording_key(laboratory.build_prompt(setup), temperature, max_tokens,
                                                       repetition)
                        self.assertIn(key, recorded.answers)

    def test_interface_sends_and_shows_the_answers(self) -> None:
        interface = prompt_lab.PromptLabInterface(laboratory.RecordedPromptRunner())
        try:
            interface.cycle_task()  # Resumir: the summary is longer than the 8-token limit
            interface.cycle_max_tokens()
            interface.send_repeated()
            self.assertEqual(len(interface.answers), laboratory.REPETITIONS)
            self.assertTrue(all(answer.finish_reason == "length" for answer in interface.answers))
            self.assertIn("gravado", interface.status.get_text())
        finally:
            plt.close(interface.figure)


class VisionTests(unittest.TestCase):
    def test_trainer_photo_is_offered_only_once_generated(self) -> None:
        with patch.object(vision, "generated_image", return_value=None):
            self.assertEqual(vision.available_images(), vision.IMAGES)
            with self.assertRaisesRegex(FileNotFoundError, "ainda não gerada"):
                vision.image_path(vision.PHOTO)
        with patch.object(vision, "generated_image", return_value=Path("foto.png")):
            self.assertEqual(vision.available_images()[-1], vision.PHOTO)

    def test_every_image_and_request_is_recorded(self) -> None:
        recorded = vision.RecordedVisionRunner()
        for image in vision.available_images():
            for request in vision.REQUESTS:
                self.assertTrue(recorded.run(image, request).text)
                self.assertIn("português europeu", vision.request_text(image, request))

    def test_interface_asks_in_the_background_and_shows_the_answer(self) -> None:
        with patch.dict(os.environ, {"FORMACAO_ML_NO_PAUSE": "1"}):
            interface = vision_exercise.VisionInterface(vision.RecordedVisionRunner())
            try:
                interface.next_image()
                interface.next_request()
                interface.ask()
                self.assertIn("Linha 2", interface.answer_text.get_text())
            finally:
                plt.close(interface.figure)


class AutoregressiveGenerationTests(unittest.TestCase):
    def test_greedy_choices_grow_the_context_until_the_end_token(self) -> None:
        source = proximo_token.RecordedNextTokenSource()
        interface = next_token.NextTokenInterface(source)
        try:
            for _ in range(next_token.MAX_NEW_TOKENS):
                interface.choose_greedy()
            self.assertTrue(interface.context.startswith(next_token.CONTEXTS[0]))
            self.assertGreater(len(interface.generated), 2)
            self.assertTrue(interface.step.is_end or len(interface.generated) == next_token.MAX_NEW_TOKENS)
            interface.undo()
            self.assertFalse(interface.step.is_end)
        finally:
            plt.close(interface.figure)

    def test_unrecorded_sample_keeps_the_previous_sentence(self) -> None:
        step = proximo_token.NextTokenStep("x", (proximo_token.TokenOption(" a", 0.6),), False, "teste")
        source = FakeSource({"A produção foi retomada após": step})
        interface = next_token.NextTokenInterface(source)
        try:
            interface.choose_sample()
            self.assertEqual(interface.generated, [])
            self.assertIs(interface.step, step)
            self.assertIn("não há resposta gravada", interface.message)
        finally:
            plt.close(interface.figure)

    def test_every_prepared_context_is_recorded(self) -> None:
        source = proximo_token.RecordedNextTokenSource()
        for context in next_token.CONTEXTS:
            self.assertTrue(source.fetch(context).options)


class FakeSource:
    """Serve fixed steps and fail like the recording for anything else."""

    def __init__(self, steps: dict) -> None:
        self.steps = steps

    def fetch(self, context: str):
        if context not in self.steps:
            raise proximo_token.NextTokenUnavailable("Não há gravação para este contexto.")
        return self.steps[context]


class SamplingRuleTests(unittest.TestCase):
    def test_temperature_concentrates_or_spreads_the_same_candidates(self) -> None:
        probabilities = np.array([0.45, 0.25, 0.15, 0.10, 0.05])
        cold = proximo_token.apply_temperature(probabilities, 0.6)
        hot = proximo_token.apply_temperature(probabilities, 1.4)

        np.testing.assert_allclose(proximo_token.apply_temperature(probabilities, 1.0), probabilities / probabilities.sum())
        self.assertAlmostEqual(float(cold.sum()), 1.0)
        self.assertGreater(cold[0], probabilities[0])
        self.assertLess(hot[0], probabilities[0])
        with self.assertRaisesRegex(ValueError, "temperatura"):
            proximo_token.apply_temperature(probabilities, 0)

    def test_top_p_keeps_the_smallest_prefix_reaching_the_threshold(self) -> None:
        probabilities = np.array([0.25, 0.45, 0.15, 0.10, 0.05])
        np.testing.assert_array_equal(
            proximo_token.apply_top_p(probabilities, 0.8), [True, True, True, False, False],
        )
        self.assertTrue(proximo_token.apply_top_p(probabilities, 1.0).all())
        np.testing.assert_array_equal(proximo_token.apply_top_p(probabilities, 0.1), [False, True, False, False, False])

    def test_sampling_only_returns_kept_candidates(self) -> None:
        options = tuple(proximo_token.TokenOption(text, p) for text, p in ((" a", 0.5), (" b", 0.3), (" c", 0.2)))
        step = proximo_token.NextTokenStep("ctx", options, False, "teste")
        random = np.random.default_rng(0)
        draws = {proximo_token.sample_candidate(step, 1.0, 0.6, random) for _ in range(200)}

        self.assertEqual(draws, {0, 1})
        self.assertAlmostEqual(step.other_probability, 0.0)


class LmStudioParsingTests(unittest.TestCase):
    def test_choice_is_ranked_and_byte_fragments_are_left_out(self) -> None:
        choice = {
            "finish_reason": "length",
            "logprobs": {"content": [{"top_logprobs": [
                {"token": " um", "bytes": [32, 117, 109], "logprob": math.log(0.2)},
                {"token": " uma", "bytes": [32, 117, 109, 97], "logprob": math.log(0.3)},
                {"token": "�", "bytes": [195], "logprob": math.log(0.1)},
            ]}]},
        }
        step = proximo_token.parse_choice("ctx", choice, "ao vivo")

        self.assertEqual([option.text for option in step.options], [" uma", " um"])
        self.assertAlmostEqual(step.other_probability, 0.5)

    def test_stop_without_candidates_is_the_end_token(self) -> None:
        step = proximo_token.parse_choice("ctx.", {"finish_reason": "stop", "logprobs": None}, "ao vivo")
        self.assertTrue(step.is_end)

    def test_unreachable_server_reports_the_address(self) -> None:
        with patch.object(lm_studio, "BASE_URL", "http://127.0.0.1:9"):
            with self.assertRaisesRegex(lm_studio.LmStudioError, "127.0.0.1:9"):
                lm_studio.post_json("/v1/chat/completions", {}, timeout=1.0)
            self.assertFalse(lm_studio.is_model_available(lm_studio.TEXT_MODEL))

    def test_live_source_falls_back_to_the_recording(self) -> None:
        class BrokenLive:
            def fetch(self, context: str):
                raise lm_studio.LmStudioError("sem servidor")

        recorded = proximo_token.RecordedNextTokenSource()
        source = proximo_token.FallbackNextTokenSource(BrokenLive(), recorded)
        step = source.fetch(next_token.CONTEXTS[0])

        self.assertTrue(step.source.startswith("gravado"))
        self.assertIsNone(source.live)


if __name__ == "__main__":
    unittest.main()
