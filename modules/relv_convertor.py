# -*- coding: utf-8 -*-
"""
This module takes in a list of scores and distribute them into discrete classes (relevance labels).
"""
from typing import List, Tuple
import jenkspy
import numpy as np


class RelvConvertor():
    """RelvConvertor object converts raw scores (from ElasticSearch) into discrete classes

    Attributes:
        relv_mode (str):
            Specifies the method used to convert ElasticSearch scores to class labels.
            Currently supports "jenks" and "percentile".
            "jenks": uses Jenks natural breaks optimization algorithm to split list
            of scores into `jenks_nb_class` number of intervals. Each interval is
            then assigned an integer label. Higher integer label corresponds to
            interval with higher ES scores.
            (https://en.wikipedia.org/wiki/Jenks_natural_breaks_optimization)
            "percentile": assigns scores in the top `n_percentile` percentile a label of 1,
            0 otherwise.
        jenks_nb_class (int): Specifies the number of intervals when mode = "jenks"
        n_percentile (int): Specifies the threshold for percentile mode
    """

    relv_mode = 'jenks'
    jenks_nb_class = 5
    n_percentile = 25

    def __init__(
            self,
            scores: List[float],
            normalized: bool = False,
            **kwargs):
        """constructor

        Args:
            scores (list(float)): A list which contains search scores (usually BM25 score) of
            retrieved documents.
            normalized (bool): indicates whether scores were normalized to [0.0, 1.0].
            If normalized is false, the scores will be normalized. Default: False
            **relv_mode (str): specifies the method used to convert scores. Supports "jenks"
            and "percentile". Default: "jenks"
            **jenks_nb_class (int): Number of intervals for "jenks" mode. Default: 5
            **n_percentile (int): cutoff percentile for "percentile" mode. Default: 25

        Raises:
            TypeError: If jenks_nb_class is not an integer.
            ValueError: If jenks_nb_class is less than 2
            TypeError: If n_percentile is not integer.
            ValueError: If n_percentile > 100 or < 0.
            Exception: If an unsupported relv_mode is specified.
        """
        self.scores = scores

        if not normalized:
            self.scores = self.normalize(scores)

        relv_mode = kwargs.get('relv_mode', self.relv_mode).lower()
        if relv_mode == "jenks":
            jenks_nb_class = kwargs.get('jenks_nb_class', self.jenks_nb_class)

            if not isinstance(jenks_nb_class, int):
                raise TypeError("jenks_nb_class has to be a positive integer.")
            if jenks_nb_class < 2:
                raise ValueError("Number of classes must be at least 2.")

            # A hack which ensures that the first interval starts from 0.0
            np.append(self.scores, [0.0])
            self.intervals = self.jenks_intervals(scores, jenks_nb_class)

        elif relv_mode == "percentile":
            n_percentile = kwargs.get('n_percentile', self.n_percentile)

            if not isinstance(n_percentile, int):
                raise TypeError("n_percentile has to be a positive integer.")
            if n_percentile > 100 or n_percentile < 0:
                raise ValueError("n_percentile must be between 0 - 100.")

            self.intervals = self.percentile_intervals(
                self.scores, kwargs['n_percentile'])
        else:
            raise Exception("Mode: %s not supported")

    @staticmethod
    def normalize(scores: List[float]) -> List[float]:
        """normalize scores to the range 0.0 to 1.0

        Args:
            scores (list(float)): A list which contains search scoresof retrieved documents.

        Raises:
            TypeError (float): If a score is not of the type float.

        Returns:
            list(float): List of normalized scores
        """

        max_score = 0
        for score in scores:
            if not isinstance(score, float):
                raise TypeError("Scores can only contain float values")
            if score > max_score:
                max_score = score
        max_score = max(scores)
        return [score / max_score for score in scores]

    @staticmethod
    def jenks_intervals(scores: List[float], nb_class: int) -> Tuple[float]:
        """A wrapper static method which uses jenkspy (https://github.com/mthh/jenkspy)
        to get natural breaks

        Args:
            scores (list(float)): A list which contains search scores of retrieved documents.
            **nb_class (int): Number of intervals

        Returns:
            tuple(float): break values
        """

        return jenkspy.jenks_breaks(scores, nb_class)

    @staticmethod
    def percentile_intervals(
            scores: List[float],
            n_percentile: int) -> Tuple[float]:
        """A static method which returns break values using the percentile method.

        Note:
            All scores in the top `n_percentile` percentile will be assigned relevance label of 1,
            0 otherwise

        Args:
            scores (list(float)): A list which contains search scores of retrieved documents.
            **n_percentile (int): threshold percentile.

        Raises:
            ValueError: If score is not between 0.0 and 1.0

        Returns:
            tuple(float): break values
        """
        for score in scores:
            if score < 0.0 or score > 1.0:
                raise ValueError("Scores must be between 0.0 and 1.0.")

        return (
            0.0,
            np.percentile(
                scores,
                100 - n_percentile),
            1.0)

    def _get_relevance(self, doc_score: float) -> int:
        """get the relevance label of doc_score

        Args:
            doc_score (float): a document score normalized to the range [0.0, 1.0]

        Raises:
        TypeError: If doc_score is not float.
        ValueError: If doc_score is not between 0.0 and 1.0

        Returns:
            int: relevance label based on precalculated self.intervals.
        """
        if not isinstance(doc_score, float):
            raise TypeError("doc_score must be float.")
        if doc_score < 0.0 or doc_score > 1.0:
            raise ValueError("doc_scores must be between 0.0 and 1.0.")

        relv = -1
        for i in range(len(self.intervals) - 1):
            if self.intervals[i] <= doc_score < self.intervals[i + 1]:
                relv = i
        return len(self.intervals) - 2 if relv == -1 else relv

    def get_relevance_labels(self) -> List[int]:
        """returns calculated relevance labels

        Returns:
            list(int): A list of relevances labels for self.scores (normalized)
        """
        return [self._get_relevance(score) for score in self.scores]
