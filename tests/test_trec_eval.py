import os
import unittest
from context import modules


class TestTrecEval(unittest.TestCase):
    """This suite of tests assume that trec_eval is downloaded and compiled"""
    @classmethod
    def setUp(self):
        script_path = os.path.dirname(os.path.abspath(__file__))
        self.metrics_file = os.path.join(
            script_path, 'test_data/default.metrics')

        with open(self.metrics_file) as metrics_f:
            metrics = metrics_f.read().split('\n')[5:-2]
            self.metrics_dict = {}
            for metric in metrics:
                metric_name, _, metric_value = metric.split('\t')
                self.metrics_dict[metric_name.strip()] = float(metric_value)

        self.qrel_file = os.path.join(script_path, 'test_data/default.qrel')
        self.res_file = os.path.join(script_path, 'test_data/default.res')

        self.trec_eval = modules.TrecEval(self.qrel_file, self.res_file)

    def test_get_metrics(self):
        """test get_metrics"""
        metrics = self.trec_eval.get_metrics()
        for metric_name in self.metrics_dict:
            self.assertEqual(
                self.metrics_dict[metric_name],
                metrics[metric_name])
