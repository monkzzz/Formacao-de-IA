import unittest

from digitlab.words_benchmark import edit_distance, metrics


class WordMetricTests(unittest.TestCase):
    def test_edits_include_insertions_deletions_and_substitutions(self):
        self.assertEqual(edit_distance("kitten", "sitting"), 3)
        self.assertEqual(edit_distance("", "word"), 4)
        self.assertEqual(edit_distance(["one", "two"], ["one", "three"]), 1)

    def test_character_and_word_rates_use_their_own_denominators(self):
        measured = metrics([{"expected": "cat dog", "predicted": "cat dogs", "elapsed_ms": 5}])
        self.assertAlmostEqual(measured["character_error_rate"], 1 / 7)
        self.assertAlmostEqual(measured["word_error_rate"], 1 / 2)
        self.assertEqual(measured["exact_matches"], 0)
