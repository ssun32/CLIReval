import unittest
import numpy as np
import jenkspy
from context import modules


class TestTrecEval(unittest.TestCase):

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
        relv_convertor = modules.RelvConvertor(scores, normalized=False)
        np.testing.assert_almost_equal(relv_convertor.scores, norm_scores)
        np.testing.assert_almost_equal(
            relv_convertor.normalize(scores), norm_scores)

        with self.assertRaises(TypeError):
            relv_convertor.normalize(["1.0"])

