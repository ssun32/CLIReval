#!/usr/bin/env python3
import sys
import json
import logging
import tempfile
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from tqdm import tqdm
from .relv_utils import normalize_bm25_scores, RelvConvertor


# hide elasticsearch logger messages
logging.getLogger('elasticsearch').setLevel(50)


class Search():
    # a default index name used for all elasticsearch operations
    INDEX = 'mt2ir'

    def __init__(
            self,
            ref_iterable,
            mt_iterable,
            query_iterable,
            **kwargs):

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
                raise Exception("query_mode: unique_term is not supported when relv_mode = query_in_document")
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
        return self.tmp_qrel_f, self.tmp_res_f

    def get_terms(self, doc_iterable):
        terms = {}
        doc_ids = [doc_id for doc_id, _ in doc_iterable]
        tfs = self.es.mtermvectors(index='mt2ir', doc_type = "doc", ids = doc_ids, fields="doc_text", field_statistics=False, term_statistics=False)
        for doc in tfs['docs']:
            for term in doc['term_vectors']['doc_text']['terms']:
                terms[term] = 1
        terms = terms.keys()

        return list(zip(range(len(terms)), terms))

    def create_qrel_file(
            self,
            query_iterable,
            doc_iterable,
            search_results,
            tmp_f,
            **kwargs):
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
            # normalize bm25 scores
            search_results_d = normalize_bm25_scores(search_results)
            doc_ids = [doc_id for doc_id, _ in doc_iterable]

            for query_id, _ in tqdm(query_iterable):
                query_id = str(query_id)

                scores = np.array([search_results_d.get(
                    (query_id, str(doc_id)), 0.0) for doc_id in doc_ids])
                relv_convertor = RelvConvertor(scores, **kwargs)

                for doc_id in doc_ids:
                    # convert document bm25 score to a relevance judgment
                    doc_score = search_results_d.get((query_id, doc_id), 0.0)
                    relv = relv_convertor.get_relevance(doc_score)

                    # output to qrel file
                    print(
                        "%s\t0\t%s\t%s" %
                        (query_id, doc_id, relv), file=tmp_f)

    def create_res_file(self, results, tmp_f):
        current_qid = ''
        rank = 0
        for query_id, doc_id, score, _ in results:
            if query_id != current_qid:
                rank = 0
            print(
                "%s\tQ0\t%s\t%s\t%.5f\tSTANDARD" %
                (query_id, doc_id, rank, score), file=tmp_f)
            rank += 1

    def recreate_index(self, analyzer):
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
        return self.es

    # add all documents in doc_iterables to elasticsearch index

    def bulk_index(self, doc_iterable):
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
        # to do handle errors here
        errors = helpers.bulk(
            self.es,
            make_bulk_json(doc_iterable),
            refresh=True,
            request_timeout=60)
        return errors[0]

    def search(self, query_iterable):
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
                search_results.append(
                    (query_id, hit['_id'], hit['_score'], response['hits']['max_score']))

        if no_hit_count:
            logging.warning("%d queries have 0 search hit", no_hit_count)

        return search_results

    def index(self, doc_iterable):
        logging.info("Bulk indexing %i documents...", len(doc_iterable))
        self.recreate_index(self.analyzer)
        success_counts = self.bulk_index(doc_iterable)

        # raise exception if index operation fails"
        if success_counts != len(doc_iterable):
            raise (
                "Number of documents in ElasticSearch Index(%s) != Number of documents provided (%s)" %
                (success_counts, len(doc_iterable)))

    def index_and_search(self, query_iterable, doc_iterable):
        self.index(doc_iterable)
        return self.search(query_iterable)
