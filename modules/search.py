# -*- coding: utf-8 -*-
"""
CLIREVAL
"""
from typing import List, Tuple
import json
import logging
import tempfile
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from tqdm import tqdm
from .relv_convertor import RelvConvertor


# hide elasticsearch logger messages
logging.getLogger('elasticsearch').setLevel(50)


class Search():
    """ Contains methods to index and search a ElasticSearch server"""

    # a default index name used for all elasticsearch operations
    INDEX = 'clireval'

    def __init__(
            self,
            ref_iterable: List[Tuple[str, str]],
            mt_iterable: List[Tuple[str, str]],
            query_iterable: List[Tuple[str, str]],
            **kwargs):
        """ Constructor of Search object

        This __init__ does the following:
            1) Index the documents in ref_iterable.
            2) If query_mode = unique_terms, then get vocabularies from ElasticSearch
            term vector
            3) Execute queries in query_iterable
            4) Convert search results to relevance labels
            5) Write results to a tmp qrel file
            6) Index the documents in mt_iterable
            7) Execulte queries in query_iterable
            8) Write results to a tmp res file

        Args:
            ref_iterable (list(tuple(str, str))): List of reference doc tuples -> (doc id, doc text)
            mt_iterable (list(tuple(str, str))): List of translated doc tuples -> (doc id, doc text)
            query_iterable (list(tuple(str, str))): List of query tuples -> (query id, query text)
            **port (int): ElasticSearch server port
            **analyzer (str): ElasticSearch analyzer
            **n_ret (int): Maximum number of documents to return per query
        """

        self.es = Elasticsearch(port=kwargs['port'], timeout=500)
        self.analyzer = kwargs['analyzer']
        self.n_ret = kwargs['n_ret']

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_qrel_f, \
                tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_res_f:
            self.tmp_qrel_f = tmp_qrel_f
            self.tmp_res_f = tmp_res_f

            # query_mode and relv_mode
            query_mode = kwargs['query_mode'].lower()
            relv_mode = kwargs['relv_mode'].lower()

            logging.info(
                "Step 1: generating qrels file using reference translations (mode: %s)",
                relv_mode)

            # if mode is not query_in_document then get search results from
            # ElasticSearch
            if relv_mode != "query_in_document":
                self.index(ref_iterable)
                if query_mode == "unique_terms":
                    query_iterable = self.get_terms(ref_iterable)
                ref_search_results = self.search(query_iterable)
            elif relv_mode == "query_in_document" and query_mode == "unique_terms":
                raise Exception(
                    "query_mode: unique_term is not supported when relv_mode = query_in_document")
            else:
                ref_search_results = None

            # create the relevance file
            logging.info(
                "Calculating relevance judgments and writing to %s",
                tmp_qrel_f.name)
            self.create_qrel_file(
                query_iterable,
                ref_iterable,
                ref_search_results,
                tmp_qrel_f,
                **kwargs)

            logging.info(
                "Step 2: generating results file using translated documents")
            # Step 2, generate result file with machine translated documents
            mt_search_results = self.index_and_search(
                query_iterable, mt_iterable)
            logging.info(
                "Writing search results to %s",
                tmp_res_f.name)
            self.create_res_file(mt_search_results, tmp_res_f)

    def get_qrel_and_res_files(self):
        """get qrel and res file objects

        returns:
            (file-like object): temp qrel file
            (file-like object): temp res file
        """
        return self.tmp_qrel_f, self.tmp_res_f

    def get_terms(
            self, doc_iterable: List[Tuple[str, str]]) -> List[Tuple[int, str]]:
        """ get unique terms across all documents

        args:
            doc_iterable (list(tuple(str, str))): List of doc tuples -> (doc id, doc text)
        """
        terms = {}
        doc_ids = [doc_id for doc_id, _ in doc_iterable]
        tfs = self.es.mtermvectors(
            index='mt2ir',
            doc_type="doc",
            ids=doc_ids,
            fields="doc_text",
            field_statistics=False,
            term_statistics=False)

        for doc in tfs['docs']:
            for term in doc['term_vectors']['doc_text']['terms']:
                terms[term] = 1
        terms = terms.keys()

        return list(zip(range(len(terms)), terms))

    @staticmethod
    def create_qrel_file(
            query_iterable: List[Tuple[str, str]],
            doc_iterable: List[Tuple[str, str]],
            search_results: List[Tuple[str, str, float]],
            tmp_f,
            **kwargs):
        """Create trec_eval qrel file

        Args:
            query_iterable (list(tuple(str, str))): List of query tuples -> (query id, query text)
            doc_iterable (list(tuple(str, str))): List of doc tuples -> (doc id, doc text)
            search_results (list(tuple(str, str, float))): List of result tuples
            -> (query id, doc id, score)
            tmp_f (file-like object): A file-like object to temporary file
        """

        if kwargs["relv_mode"] == "query_in_document":
            for query_id, query in tqdm(query_iterable):
                for doc_id, doc in doc_iterable:
                    print(query)
                    relv = 1 if query in doc else 0
                    # output to qrel file
                    print(
                        "%s\t0\t%s\t%s" %
                        (query_id, doc_id, relv), file=tmp_f)

        else:
            search_results_d = {(str(query_id), str(doc_id)): score
                                for query_id, doc_id, score in search_results}
            doc_ids = [doc_id for doc_id, _ in doc_iterable]

            for query_id, _ in tqdm(query_iterable):
                query_id = str(query_id)

                scores = np.array([search_results_d.get(
                    (query_id, str(doc_id)), 0.0) for doc_id in doc_ids])
                relv_convertor = RelvConvertor(scores, **kwargs)
                relv_labels = relv_convertor.get_relevance_labels()

                for relv, doc_id in zip(relv_labels, doc_ids):
                    # output to qrel file
                    print(
                        "%s\t0\t%s\t%s" %
                        (query_id, doc_id, relv), file=tmp_f)

    @staticmethod
    def create_res_file(results: List[Tuple[str, str, float]], tmp_f):
        """Creates trec_eval results file

        Args:
            results (list(tuple(str, str, float))): List of result tuples
            -> (query id, doc id, bm25 scores)
            tmp_f (file-like object): A file-like object to temporary file
        """
        current_qid = ''
        rank = 0
        for query_id, doc_id, score in results:
            if query_id != current_qid:
                rank = 0
            print(
                "%s\tQ0\t%s\t%s\t%.5f\tSTANDARD" %
                (query_id, doc_id, rank, score), file=tmp_f)
            rank += 1

    def recreate_index(self, analyzer: str):
        """ deletes previous index and create a new index

        args:
            analzyer (str): ElasticSearch Analyzer
        """
        index_settings = '''{
        "settings" : {
            "index" : {
                "number_of_shards" : 1,
                "number_of_replicas" : 1
                }
            }
        }'''

        mapping = '''{
          "properties": {
            "doc_text": {
              "type": "text",
              "analyzer": \"%s\",
              "search_analyzer": \"%s\"
            }
          }
        }''' % (analyzer, analyzer)

        # delete the existing index
        if self.es.indices.exists(index=self.INDEX):
            self.es.indices.delete(index=self.INDEX)

        # create a elasticsearch index with the name self.INDEX
        self.es.indices.create(index=self.INDEX, body=index_settings)

        # put index mapping
        self.es.indices.put_mapping(
            index=self.INDEX, doc_type='doc', body=mapping)

    # add all documents in doc_iterables to elasticsearch index

    def bulk_index(self, doc_iterable: List[Tuple[str, str]]) -> int:
        """ bulk index documents into ElasticSearch Server

        args:
            doc_iterable (list(tuple(str, str))): List of document tuples -> (doc id, doc text)

        returns:
            (int): Number of successful index operations
        """

        # helper function to create bulk json string
        def make_bulk_json(doc_iterable):
            json_l = []
            for doc_id, doc_text in doc_iterable:
                j = {
                    "doc": {
                        "doc_text": '\n'.join(doc_text)
                    },
                    "_id": doc_id,
                    "_index": self.INDEX,
                    "_type": "doc",
                    "_op_type": "update",
                    "doc_as_upsert": True
                }
                json_l.append(j)
            return json_l

        # tuple of number-successes (int) and a list of errors
        # to do: handle errors
        errors = helpers.bulk(
            self.es,
            make_bulk_json(doc_iterable),
            refresh=True,
            request_timeout=60)
        return errors[0]

    def search(
            self, query_iterable: List[Tuple[str, str]]) -> List[Tuple[str, str, float]]:
        """ Execute queries in query_iterable and return results

        Args:
            query_iterable (list(tuple(str, str))): List of query tuples -> (query id, query text)

        Returns:
            list(tuple(str, str, float)): list of result tuples -> (query id, doc id, bm25 score)
        """
        no_hit_count = 0
        logging.info(
            "Getting search results from ElasticSearch (%i queries)...",
            len(query_iterable))
        search_results = []
        for query_id, query in tqdm(query_iterable):
            j = {}
            j['size'] = self.n_ret
            j['query'] = {
                "simple_query_string": {
                    "query": "%s" % query,
                    "fields": ["doc_text"]
                }
            }
            j['track_scores'] = True
            response = self.es.search(index=self.INDEX,
                                      body=json.dumps(j),
                                      sort=["_score:desc", "_uid:asc"],
                                      request_timeout=500)

            if len(response['hits']['hits']) == 0:
                no_hit_count += 1
            for hit in response['hits']['hits']:
                search_results.append((query_id, hit['_id'], hit['_score']))

        if no_hit_count:
            logging.warning("%d queries have 0 search hit", no_hit_count)

        return search_results

    def index(self, doc_iterable: List[Tuple[str, str]]):
        """ bulk index documents in doc_iterable

        Raises:
            Exception: If number of successfully indexed documents != number of documents
            in doc_iterable

        Args:
            doc_iterable (list(tuple(str, str))): A list of tuples -> (doc id, doc text)
        """
        logging.info("Bulk indexing %i documents...", len(doc_iterable))
        self.recreate_index(self.analyzer)
        success_counts = self.bulk_index(doc_iterable)

        # raise exception if index operation fails"
        if success_counts != len(doc_iterable):
            raise (
                """Number of documents in ElasticSearch Index(%s)
                != Number of documents provided (%s)""" %
                (success_counts, len(doc_iterable)))

    def index_and_search(
            self, query_iterable: List[Tuple[str, str]],
            doc_iterable: List[Tuple[str, str]]) -> List[Tuple[str, str, float]]:
        """ index with documents in doc_iterable and search with queries in query_iterable

        Args:
            query_iterable (list(tuple(str, str))): List of query tuples -> (query id, query text)

        Returns:
            (list(tuple(str, str, float))): returns results from self.search
        """
        self.index(doc_iterable)
        return self.search(query_iterable)
