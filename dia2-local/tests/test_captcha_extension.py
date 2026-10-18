import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from digitlab.captcha_extension import balanced, eligible, final_test
from digitlab.captcha_extension_data import CONDITIONS, SOURCES, make_set, render


class CaptchaExtensionTests(unittest.TestCase):
    def test_integer_coverage_gain_does_not_allow_confident_errors_or_clean_regression(self):
        raw = {"count": 5400, "accuracy": .98, "correct_above_90_count": 5000,
               "loss": .08, "brier": .02, "ece_10_bins": .01, "wrong_above_90_count": 3}
        baseline = {"raw": raw, "mnist": {"accuracy": .993}, "emnist": {"accuracy": .99}, "bridge": {"accuracy": .97}}
        candidate = copy.deepcopy(baseline)
        candidate["raw"].update(loss=.07, correct_above_90_count=5026)
        self.assertFalse(eligible(candidate, baseline))
        candidate["raw"]["correct_above_90_count"] = 5027
        self.assertTrue(eligible(candidate, baseline))
        candidate["raw"]["wrong_above_90_count"] = 4
        self.assertFalse(eligible(candidate, baseline))
        candidate["raw"]["wrong_above_90_count"] = 3
        candidate["emnist"]["accuracy"] = .988
        self.assertFalse(eligible(candidate, baseline))

    def test_clean_sampler_is_balanced_reproducible_and_source_limited(self):
        labels = np.repeat(np.arange(10), 20)
        supplied = np.array([i for i in range(200) if i % 20])
        selected = balanced(labels, supplied, 100, 11)
        np.testing.assert_array_equal(selected, balanced(labels, supplied, 100, 11))
        np.testing.assert_array_equal(np.bincount(labels[selected]), np.full(10, 10))
        self.assertEqual(len(set(selected)), 100)
        self.assertTrue(set(selected) <= set(supplied))

    def test_reserved_sources_are_not_loaded_without_selection_and_browser_gate(self):
        with patch("digitlab.captcha_extension.selected", side_effect=ValueError("no eligible model")), \
                patch("digitlab.captcha_extension.load_partition") as mnist, \
                patch("digitlab.captcha_extension.extra.load_partition") as emnist:
            with self.assertRaises(ValueError):
                final_test()
            mnist.assert_not_called()
            emnist.assert_not_called()
        with patch("digitlab.captcha_extension.selected", return_value=({}, {"checkpoint_sha256": "fixed"})), \
                patch.object(Path, "exists", return_value=False), \
                patch.object(Path, "read_text", return_value=json.dumps({"status": "FAIL"})), \
                patch("digitlab.captcha_extension.load_partition") as mnist, \
                patch("digitlab.captcha_extension.extra.load_partition") as emnist:
            with self.assertRaises(ValueError):
                final_test()
            mnist.assert_not_called()
            emnist.assert_not_called()

    def test_all_source_condition_severity_cells_and_quality_bounds_are_reproducible(self):
        font = Path(__file__).resolve().parents[1] / "data/open-fonts/lato/Lato-Regular.ttf"
        if not font.exists():
            self.skipTest("Prepare the portable font fixture")
        images = np.zeros((20, 28, 28), np.uint8)
        images[:, 5:23, 11:17] = 220
        labels = np.repeat(np.arange(10), 2)
        supplied = np.arange(1, 20, 2)
        x, y, records = make_set(images, labels, supplied, images, labels, supplied, [font], 540, 17)
        cells = {(r["label"], r["source"], r["condition"], r["severity"]) for r in records}
        self.assertEqual(len(cells), 10 * len(SOURCES) * len(CONDITIONS) * 3)
        self.assertEqual(x.shape, (540, 1, 64, 64))
        self.assertTrue(np.isfinite(x).all())
        self.assertTrue(all(r["source_index"] in supplied for r in records if r["source"] != "printed"))
        self.assertTrue(all(r["glyph_mass_retained"] >= .99 and r["erased_glyph_fraction"] <= .08 for r in records))
        a, qa = render(np.random.default_rng(9), 4, images[9], font, "mixed", 2)
        b, qb = render(np.random.default_rng(9), 4, images[9], font, "mixed", 2)
        np.testing.assert_array_equal(np.asarray(a), np.asarray(b))
        self.assertEqual(qa, qb)
