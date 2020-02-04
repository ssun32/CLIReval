import unittest
import numpy as np
import jenkspy
from context import modules


class TestRelvConverter(unittest.TestCase):

    def test_normalize(self):
        """test whether scores are normalized to the range [0.0, 1.0]"""
        scores = [0.77, 30.788, 71.48, 101.5, 123.77, 144.1]
        norm_scores = [
            0.0053435114503816794,
            0.21365718251214436,
            0.49604441360166557,
            0.7043719639139486,
            0.8589174184594032,
            1.0]
        relv_converter = modules.RelvConverter(scores, normalized=False)
        np.testing.assert_almost_equal(relv_converter.scores, norm_scores)
        np.testing.assert_almost_equal(
            relv_converter.normalize(scores), norm_scores)

        with self.assertRaises(TypeError):
            relv_converter.normalize(["1.0"])

    def test_init(self):
        """Tests for the __init__ function"""
        scores = [0.77, 30.788, 71.48, 101.5, 123.77, 144.1]
        with self.assertRaises(ValueError):
            modules.RelvConverter(
                scores, **{"jenks_nb_class": -1})
        with self.assertRaises(TypeError):
            modules.RelvConverter(
                scores, **{"jenks_nb_class": "2"})
        with self.assertRaises(ValueError):
            modules.RelvConverter(
                scores, **{"relv_mode": "percentile", "n_percentile": -1})
        with self.assertRaises(ValueError):
            modules.RelvConverter(
                scores, **{"relv_mode": "percentile", "n_percentile": 101})
        with self.assertRaises(TypeError):
            modules.RelvConverter(
                scores, **{"relv_mode": "percentile", "n_percentile": "2"})
        with self.assertRaises(Exception):
            modules.RelvConverter(
                scores, **{"relv_mode": "UNK"})

    def test_get_jenks_intervals(self):
        """Tests for jenks intervals"""
        scores = [
            0.0053435114503816794,
            0.21365718251214436,
            0.49604441360166557,
            0.7043719639139486,
            0.8589174184594032,
            1.0]
        scores_bad_type = ["0.88", "test"]
        scores_bad_value = [0.88, -1000.0, 100001.0]

        with self.assertRaises(ValueError):
            modules.RelvConverter.get_jenks_intervals(
                scores_bad_value, nb_class=2)
        with self.assertRaises(TypeError):
            modules.RelvConverter.get_jenks_intervals(
                scores_bad_type, nb_class=2)

        jenks_breaks = jenkspy.jenks_breaks(scores, nb_class=2)
        jenks_breaks_mod = modules.RelvConverter.get_jenks_intervals(
            scores, nb_class=2)
        np.testing.assert_almost_equal(jenks_breaks, jenks_breaks_mod)

    def test_get_percentile_intervals(self):
        """Tests for percentile intervals"""
        scores = [0.0, 0.1, 0.3, 0.4, 0.6, 0.5, 0.8, 0.7, 0.9, 1.0]
        scores_bad_type = ["0.88", "test"]
        scores_bad_value = [0.88, -1000.0, 100001.0]
        percentile_intervals = modules.RelvConverter.get_percentile_intervals

        with self.assertRaises(ValueError):
            percentile_intervals(scores_bad_value, n_percentile=20)
        with self.assertRaises(TypeError):
            percentile_intervals(scores_bad_type, n_percentile=20)

        np.testing.assert_almost_equal(
            percentile_intervals(
                scores, 100),
            [0.0, 0.0, 1.0])
        np.testing.assert_almost_equal(
            percentile_intervals(
                scores, 0),
            [0.0, 1.0, 1.0])
        np.testing.assert_almost_equal(
            percentile_intervals(
                scores, 25),
            [0.0, 0.775, 1.0])
        np.testing.assert_almost_equal(
            percentile_intervals(
                scores, 50),
            [0.0, 0.55, 1.0])

    def test_get_relevance_labels(self):
        """Tests for percentile intervals"""
        scores1 = [0.0, 0.1, 0.3, 0.4, 0.6, 0.5, 0.8, 0.7, 0.9, 1.0]
        scores2 = [0.77, 30.788, 71.48, 101.5, 123.77, 144.1]

        def test_helper(scores, correct_labels, **kwargs):
            labels = modules.RelvConverter(
                scores, **kwargs).get_relevance_labels()
            self.assertEqual(labels, correct_labels)

        test_helper(scores1, [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                    **{"relv_mode": "jenks", "jenks_nb_class": 2})
        test_helper(scores2, [0, 1, 1, 1, 1, 1],
                    **{"relv_mode": "jenks", "jenks_nb_class": 2})
        test_helper(scores1, [0, 1, 1, 2, 3, 2, 4, 3, 4, 4],
                    **{"relv_mode": "jenks", "jenks_nb_class": 5})
        test_helper(scores2, [0, 1, 2, 3, 4, 4],
                    **{"relv_mode": "jenks", "jenks_nb_class": 5})
        test_helper(scores1, [0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
                    **{"relv_mode": "percentile", "n_percentile": 25})
        test_helper(scores2, [0, 0, 0, 0, 1, 1],
                    **{"relv_mode": "percentile", "n_percentile": 25})
        test_helper(scores1, [0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
                    **{"relv_mode": "percentile", "n_percentile": 50})
        test_helper(scores2, [0, 0, 0, 1, 1, 1],
                    **{"relv_mode": "percentile", "n_percentile": 50})
