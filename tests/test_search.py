import os
import unittest
from unittest import mock
import tempfile
from context import modules


class TestSearch(unittest.TestCase):
    @classmethod
    def setUp(self):
        """patch ElasticSearch module with a mock class"""
        self.es_patcher = mock.patch('modules.search.Elasticsearch')
        self.helpers_patcher = mock.patch('modules.search.helpers')

        self.elasticsearch = self.es_patcher.start()
        self.helpers = self.helpers_patcher.start()

        self.docs = [("1", "sent"), ("2", "sent"), ("3", "sent"),
                     ("4", "sent 2"), ("5", "sent 2"), ("6", "sent 2")]
        self.search_results = {"hits": {"hits":
                                        [{"_id": "1", "_score": 100.0},
                                         {"_id": "2", "_score": 80.0},
                                         {"_id": "3", "_score": 60.0},
                                         {"_id": "4", "_score": 50.0},
                                         {"_id": "5", "_score": 10.0},
                                         {"_id": "6", "_score": 0.0}
                                         ]}}

        self.term_vectors = {"docs": [{"term_vectors": {"doc_text": {"terms": ["sent"]}}},
                                      {"term_vectors": {"doc_text": {"terms": ["sent"]}}},
                                      {"term_vectors": {"doc_text": {"terms": ["sent"]}}},
                                      {"term_vectors": {"doc_text": {"terms": ["sent", "2"]}}},
                                      {"term_vectors": {"doc_text": {"terms": ["sent", "2"]}}},
                                      {"term_vectors": {"doc_text": {"terms": ["sent", "2"]}}}]}

        self.unique_terms = ["sent", "2"]

        # reference trec_eval files
        self.default_ref_res_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'test_data/default.res')
        self.default_ref_qrel_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'test_data/default.qrel')

        # mock instance methods
        self.elasticsearch.return_value.search.return_value = self.search_results
        self.elasticsearch.return_value.mtermvectors.return_value = self.term_vectors
        self.helpers.bulk.return_value = (len(self.docs), None)

        self.search_mod = modules.Search(self.docs,
                                         self.docs,
                                         self.docs)

    def tearDown(self):
        """stop mock patchers"""
        self.es_patcher.stop()
        self.helpers_patcher.stop()

    def test_init(self):

        # reference files
        script_path = os.path.dirname(os.path.abspath(__file__))
        jenks_2_res_file = os.path.join(script_path, 'test_data/jenks_2.res')
        jenks_2_qrel_file = os.path.join(script_path, 'test_data/jenks_2.qrel')
        percentile_25_res_file = os.path.join(
            script_path, 'test_data/percentile_25.res')
        percentile_25_qrel_file = os.path.join(
            script_path, 'test_data/percentile_25.qrel')
        percentile_50_res_file = os.path.join(
            script_path, 'test_data/percentile_50.res')
        percentile_50_qrel_file = os.path.join(
            script_path, 'test_data/percentile_50.qrel')
        query_in_document_res_file = os.path.join(
            script_path, 'test_data/query_in_document.res')
        query_in_document_qrel_file = os.path.join(
            script_path, 'test_data/query_in_document.qrel')
        default_unique_terms_res_file = os.path.join(
            script_path, 'test_data/default_unique_terms.res')
        default_unique_terms_qrel_file = os.path.join(
            script_path, 'test_data/default_unique_terms.qrel')
        unique_terms_percentile_res_file = os.path.join(
            script_path, 'test_data/unique_terms_percentile.res')
        unique_terms_percentile_qrel_file = os.path.join(
            script_path, 'test_data/unique_terms_percentile.qrel')

        def test_helper(ref_qrel_file, ref_res_file, **kwargs):
            search = modules.Search(self.docs, self.docs, self.docs, **kwargs)
            qrel_file, res_file = search.get_qrel_and_res_files()

            with open(qrel_file) as f_qrel, open(res_file) as f_res, \
                    open(ref_qrel_file) as f_qrel_ref, open(ref_res_file) as f_res_ref:
                self.assertEqual(f_qrel.read(), f_qrel_ref.read())
                self.assertEqual(f_res.read(), f_res_ref.read())

        # relv_mode:jenks query_mode:sentences nb_class:5
        test_helper(self.default_ref_qrel_file,
                    self.default_ref_res_file,
                    **{"relv_mode": "jenks", "query_mode": "sentences"})

        # relv_mode:jenks query_mode:sentences nb_class:2
        test_helper(jenks_2_qrel_file,
                    jenks_2_res_file,
                    **{"relv_mode": "jenks",
                       "jenks_nb_class": 2,
                       "query_mode": "sentences"})

        # relv_mode:percentile query_mode:sentences n_percentile:25
        test_helper(percentile_25_qrel_file,
                    percentile_25_res_file,
                    **{"relv_mode": "percentile", "query_mode": "sentences"})

        # relv_mode:percentile query_mode:sentences n_percentile:50
        test_helper(percentile_50_qrel_file,
                    percentile_50_res_file,
                    **{"relv_mode": "percentile",
                       "n_percentile": 50,
                       "query_mode": "sentences"})

        # relv_mode:query_in_document query_mode:sentences
        test_helper(query_in_document_qrel_file,
                    query_in_document_res_file,
                    **{"relv_mode": "query_in_document",
                       "query_mode": "sentences"})

        # relv_mode:jenks query_mode:unique_terms nb_class:5
        test_helper(default_unique_terms_qrel_file,
                    default_unique_terms_res_file,
                    **{"relv_mode": "jenks", "query_mode": "unique_terms"})

        # relv_mode:percentile query_mode:unique_terms n_percentile:25
        test_helper(unique_terms_percentile_qrel_file,
                    unique_terms_percentile_res_file,
                    **{"relv_mode": "percentile", "query_mode": "unique_terms"})

        # query_mode = unique_terms is not supported when relv_mode =
        # query_in_document
        with self.assertRaises(Exception):
            test_helper(None,
                        None,
                        **{"relv_mode": "query_in_document",
                           "query_mode": "unique_terms"})

    def test_create_qrel_file(self):
        """test whether a valid tre_eval qrel file is created"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_f:
            search_results = self.search_mod.search(self.docs)
            self.search_mod.create_qrel_file(
                self.docs, self.docs, search_results, tmp_f)

        with open(tmp_f.name) as f1, open(self.default_ref_qrel_file) as f2:
            self.assertEqual(f1.read().strip(), f2.read().strip())

    def test_create_res_file(self):
        """test whether a valid trec_eval res file is created"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_f:
            search_results = self.search_mod.search(self.docs)
            self.search_mod.create_res_file(search_results, tmp_f)

        with open(tmp_f.name) as f1, open(self.default_ref_res_file) as f2:
            self.assertEqual(f1.read().strip(), f2.read().strip())

    def test_get_terms(self):
        """test whether get_terms can retrieve term vectors from elasticsearch"""
        terms = self.search_mod.get_terms(self.docs)
        terms = set([term[-1] for term in terms])
        self.assertEqual(terms, set(self.unique_terms))

    def test_search(self):
        """test search results on mock queries and docs"""

        search_results = self.search_mod.search(self.docs)
        for doc_id1, _ in self.docs:
            for i, (doc_id2, _) in enumerate(self.docs):
                self.assertIn(
                    (doc_id1,
                     doc_id2,
                     self.search_results["hits"]["hits"][i]["_score"]),
                    search_results)
