from os import path
from bs4 import BeautifulSoup as bs

class doc_parser(object):

    #constants
    SGML = 'sgml'
    TSV = 'tsv'

    def __init__(self, doc_file_path):
        self.doc_file_type = self.get_file_type(doc_file_path)

        if self.doc_file_type is self.SGML:
            self.docs = self.parse_sgml(doc_file_path)

    def get_file_type(self, file_path):
        file_ext = path.splitext(file_path)[-1]
        if file_ext.lower() in ['sgm', 'sgml']:
            return self.SGML
        elif file_ext.lower() in ['tsv']:
            return self.TSV
        else:
            return self.SGML


    def parse_sgml(self, sgml_file):
        docs = []
        with open(sgml_file) as f:
            soup = bs(f.read(), 'html.parser')
            for doc_id, doc in enumerate(soup.find_all('doc')):
                doc_text = []
                for sentence in doc.find_all('seg'):
                    doc_text.append(sentence.get_text())
                docs.append((doc_id, doc_text))
        return docs

    def get_docs(self):
        return self.docs

    def get_queries(self):
        queries = []
        for doc_id, doc_text in self.docs:
            for i, query in enumerate(doc_text):
                query_id = "%s_%i" % (doc_id, i)
                queries.append((query_id, query))
        return queries

    def get_vocab_query_iterable(self):
        df = defaultdict(dict)
        for doc_id, doc_text in self.docs:
            for i, sent in enumerate(doc_text):
                for tok in sent.split():
                    df[tok][doc_id] = 1

        q = []
        for i, k in enumerate(sorted(df.keys(), key=lambda x: len(df[x].keys()), reverse=True)[:1000]):
            q.append(("query_%s" % i, k))
        return q
