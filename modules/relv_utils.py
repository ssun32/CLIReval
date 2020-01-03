import jenkspy
import numpy as np


def normalize_bm25_scores(results):
    return {(str(query_id), str(doc_id)): score /
            max_score for query_id, doc_id, score, max_score in results}


class RelvConvertor():
    def __init__(self, scores, **kwargs):
        mode = kwargs['relv_mode'].lower()
        if mode == "jenks":
            nb_class = kwargs['jenks_nb_class']
            if nb_class < 2:
                raise Exception("Number of classes must be at least 2.")
            np.append(scores, [0.0])
            self.intervals = self.jenks_intervals(scores, nb_class)

        elif mode == "percentile":
            self.intervals = self.percentile_intervals(
                scores, kwargs['n_percentile'])

    @staticmethod
    def jenks_intervals(scores, nb_class):
        return jenkspy.jenks_breaks(scores, nb_class)

    @staticmethod
    def percentile_intervals(scores, n_percentile):
        return [
            0.0,
            np.percentile(
                scores,
                100 - n_percentile),
            1.0]

    def get_relevance(self, doc_score):
        relv = -1
        for i in range(len(self.intervals) - 1):
            if self.intervals[i] <= doc_score < self.intervals[i + 1]:
                relv = i
        return len(self.intervals) - 2 if relv == -1 else relv
