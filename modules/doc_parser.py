import logging
from os import path
from collections import defaultdict
from bs4 import BeautifulSoup as bs

class DocParser():

    # constants
    SGML = 'sgml'
    TSV = 'tsv'

    def __init__(self, doc_file_path):
        self.doc_file_type = self.get_file_type(doc_file_path)

        if self.doc_file_type == self.SGML:
            self.docs, self.dropped_docs, self.total_sents = self.parse_sgml(
                doc_file_path)
            self.total_docs = len(self.docs)
        else:
            self.docs, self.dropped_docs, self.total_sents = self.parse_tsv(
                doc_file_path)
            self.total_docs = len(self.docs)


    def get_file_type(self, file_path):
        file_ext = path.splitext(file_path)[-1][1:]
        print(file_ext)
        if file_ext.lower() in ['sgm', 'sgml']:
            return self.SGML
        elif file_ext.lower() in ['tsv']:
            return self.TSV
        else:
            return self.SGML

    @staticmethod
    def parse_sgml(sgml_file):
        dropped_docs = 0
        total_sents = 0
        docs = []
        with open(sgml_file) as input_f:
            soup = bs(input_f.read(), 'html.parser')
            for doc in soup.find_all('doc'):
                doc_id = doc.get('docid')
                doc_text = []
                for sentence in doc.find_all('seg'):
                    # if no reference is available, stop reading
                    if sentence.get_text() == "NO REFERENCE AVAILABLE":
                        dropped_docs += 1
                        break
                    total_sents += 1
                    doc_text.append(sentence.get_text())

                if doc_text:
                    docs.append((doc_id, doc_text))
        return docs, dropped_docs, total_sents

    @staticmethod
    def parse_tsv(tsv_file):
        dropped_docs = 0
        total_sents = 0
        docs = []
        tmp_docs = defaultdict(list)
        for l in open(tsv_file):
            try:
                doc_id, doc_sent = l.split('\t')
                tmp_docs[doc_id].append(doc_sent)
                total_sents += 1
            except:
                raise Exception("Unable to read tsv file")

        for doc_id, doc_text in tmp_docs.items():
            docs.append((doc_id, doc_text))
        return docs, dropped_docs, total_sents

    def get_docs(self):
        return self.docs

    def log_doc_stats(self):
        logging.info(
            "Total Document(s): %d, Total Sentence(s): %d, Dropped document(s): %d",
            self.total_docs,
            self.total_sents,
            self.dropped_docs)

    def get_queries(self):
        queries = []
        for doc_id, doc_text in self.docs:
            for i, query in enumerate(doc_text):
                query_id = "%s_%i" % (doc_id, i)
                queries.append((query_id, query))
        return queries
