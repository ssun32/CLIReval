#!/usr/bin/env python3

from collections import defaultdict
import numpy as np
import jenkspy
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from tqdm import tqdm

import os
import argparse
import json
import logging
import tempfile

logging.getLogger('elasticsearch').setLevel(50)

class search(object):
    #a default index name used for all elasticsearch operations
    INDEX = 'mt2ir'

    def __init__(self, ref_iterable, mt_iterable, query_iterable, analyzer, port=9200):

        self.es = Elasticsearch(port=port, timeout=500)
        total_docs = len(ref_iterable)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_qrel_f, \
             tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_res_f:
            self.tmp_qrel_f = tmp_qrel_f
            self.tmp_res_f = tmp_res_f

            #Step 1, create qrel file with reference translations
            ref_search_results = self.index_and_search(query_iterable, ref_iterable, analyzer)
            self.create_qrel_file(query_iterable, ref_search_results, tmp_qrel_f, total_docs)

            #Step2, create result file with machine translated documents
            mt_search_results = self.index_and_search(query_iterable, ref_iterable, analyzer)
            self.create_res_file(mt_search_results,  tmp_res_f)


    def get_qrel_and_res_files(self):
        return self.tmp_qrel_f, self.tmp_res_f


    def create_qrel_file(self, query_iterable, results, tmp_f, total_docs):
        #normalize bm25 scores
        results_d = {(str(query_id), str(doc_id)): score/max_score for query_id, doc_id, score, max_score in results}

        scores = np.array([score for k, score in results_d.items()])

        for query_id, _ in query_iterable:
            query_id = str(query_id)

            #added 0 to the scores list so that jenks intervals would start from 0.0
            scores = np.array([results_d.get((query_id, str(doc_id)), 0.0) for doc_id in range(total_docs)] + [0])
            intervals = jenkspy.jenks_breaks(scores, nb_class=5)

            r = defaultdict(int)
            for doc_id in range(total_docs):
                doc_id = str(doc_id)
                doc_score = results_d.get((query_id, doc_id), 0.0)

                relv = -1
                for c in range(5):
                    if doc_score >= intervals[c] and doc_score < intervals[c+1]:
                        relv = c
                        r[c] += 1
                    relv = 4 if relv == -1 else relv
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

        #delete the existing index
        if self.es.indices.exists(index=self.INDEX):
            self.es.indices.delete(index=self.INDEX)

        #create a elasticsearch index with the name self.INDEX
        self.es.indices.create(index=self.INDEX, body=index_settings)

        #put index mapping
        self.es.indices.put_mapping(index=self.INDEX, doc_type='doc', body=mapping)
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
        for query_id, query in tqdm(query_iterable):
            j = {}
            j['size'] = 1000
            j['query'] = {
                    "simple_query_string": {
                        "query": "%s" % query,
                        "fields": ["doc_text"]
                        }
                    }
            j['track_scores'] = True
            response = self.es.search(index = self.INDEX, 
                                 body = json.dumps(j),
                                 sort = ["_score:desc", "_uid:asc"], 
                                 request_timeout = 500)

            for hit in response['hits']['hits']:
                yield query_id, hit['_id'], hit['_score'], response['hits']['max_score']


    def index_and_search(self, query_iterable, doc_iterable, analyzer):
        self.recreate_index(analyzer)
        self.bulk_index(doc_iterable)
        return self.search(query_iterable)
