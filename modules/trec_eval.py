# -*- coding: utf-8 -*-
"""
This module contains a wrapper class for trec_eval
"""
from typing import Dict, Optional
import subprocess
import os
import json
import logging


class TrecEval():
    """ A wrapper class for trec_eval"""
    script_path = os.path.dirname(os.path.abspath(__file__))
    trec_eval_bin = os.path.join(script_path, "../external_tools/trec_eval/trec_eval")

    def __init__(self, qrel_f: str, res_f: str):
        """ Constructor which takes a qrel file and a results file
        Args:
            qrel_f (str): path of file with list of relevant documents for each query
            res_f (str): path of file with list of documents retrieved by ElasticSearch

        Raises:
            Exception: If trec_eval binary file does not exists.
        """
        self.qrel_f = qrel_f
        self.res_f = res_f
        self.metrics = None

        if not os.path.exists(self.trec_eval_bin):
            raise Exception(
                """trec_eval binary file does not exists.
                Please download using ./scripts/install_external_tools.sh""")

    def set_trec_eval_bin_path(self, bin_path: str):
        """ Change the path of the trec_eval binary file

        Args:
            bin_path (str): A string containing the path of the trec_eval binary file
        """
        self.trec_eval_bin = bin_path

    def get_metrics(self) -> Dict[str, float]:
        """ Get IR metrics using trec_eval (https://github.com/usnistgov/trec_eval)

        Returns:
            dict(str, float): Maps metric name to metric value
        """

        if not self.metrics:
            trec_eval_output = subprocess.check_output(
                [self.trec_eval_bin, "-m", "all_trec", "-M1000", self.qrel_f, self.res_f]
            ).decode('ascii')

            self.metrics = {}
            # remove first 5 items and last item
            for metric in trec_eval_output.split('\n')[5:-2]:
                metric = metric.split('\t')
                metric_name, _, metric_value = metric
                metric_name = metric_name.strip()
                metric_value = float(metric_value)
                self.metrics[metric_name] = metric_value

        return self.metrics

    def print_metrics(self, output_format: str = "tsv",
                      output_file: Optional[str] = None):
        """ print IR metrics to either a file or stdout

        Args:
            output_format (str): json or tsv
            output_file (str, optional): path to write output
        """

        if output_format.lower() == 'json':
            output_str = json.dumps(self.get_metrics())
        else:
            output_str = "\n".join(["%s\t%s" % (k, v)
                                    for k, v in self.get_metrics().items()])

        if output_file:
            with open(output_file, 'w') as fout:
                print(output_str, file=fout)
            logging.info("Evaluation results written to %s...", output_file)
        else:
            print(output_str)
