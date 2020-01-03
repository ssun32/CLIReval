from os import path
from bs4 import BeautifulSoup as bs

class DocParser():

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
