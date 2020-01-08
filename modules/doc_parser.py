# -*- coding: utf-8 -*-
"""
Document parser for MT SGML file or tsv file
"""


from typing import Tuple, List
import logging
from os import path
from collections import defaultdict
from bs4 import BeautifulSoup as bs


class DocParser():
    """Class contains various methods to read document file.
    Currently supports sgml and tsv files.

    Attributes:
        doc_file_type (str): type of input file (tsv or sgml)
        docs (list(tuple(str, str))): List of tuples -> (doc_id, doc_text)
        total_sents (int): Total number of sentences in documents
    """

    # constants
    SGML = 'sgml'
    TSV = 'tsv'

    def __init__(self, doc_file_path: str):
        """ constructor

        Args:
            doc_file_path (str): path to the document
        """
        self.doc_file_type = self.get_file_type(doc_file_path)

        try:
            if self.doc_file_type == self.SGML:
                self.docs, self.total_sents = self.parse_sgml(doc_file_path)
            else:
                self.docs, self.total_sents = self.parse_tsv(doc_file_path)
            self.total_docs = len(self.docs)
        except:
            raise Exception("Failed to parse file.")


    def get_file_type(self, file_path: str) -> str:
        """A method used to determine type of input file

        Note:
            If file does not have an extension, defaults to SGML

        Args:
            file_path (str): path of a file
        """
        file_ext = path.splitext(file_path)[-1][1:]
        if file_ext.lower() in ['sgm', 'sgml']:
            return self.SGML
        elif file_ext.lower() in ['tsv']:
            return self.TSV
        return self.SGML

    @staticmethod
    def parse_sgml(sgml_file: str) -> Tuple[List[Tuple[str, str]], int]:
        """Method used to parse sgml files

        Args:
            sgml_file (str): path to sgml file

        Raises:
            Exception: if unable to read tsv file

        Returns:
            tuple(list(tuple(str, str)), int): A list of tuples -> (doc_id, doc_text) and
            total number of sentences
        """

        total_sents = 0
        docs = []
        with open(sgml_file) as input_f:
            soup = bs(input_f.read(), 'html.parser')
            for doc in soup.find_all('doc'):
                doc_id = doc.get('docid')
                doc_text = []
                for sentence in doc.find_all('seg'):
                    total_sents += 1
                    doc_text.append(sentence.get_text())

                if doc_text:
                    docs.append((doc_id, doc_text))
        return docs, total_sents

    @staticmethod
    def parse_tsv(tsv_file: str) -> Tuple[List[Tuple[str, str]], int]:
        """ Method used to parse tsv files

        Note:
            TSV file must contain 2 columns, doc_id and doc_sent

        Args:
            tsv_file (str): path to tsv file

        Raises:
            Exception: if unable to read tsv file

        Returns:
            tuple(list(tuple(str, str)), int): A list of tuples -> (doc_id, doc_text) and
            total number of sentences
        """
        total_sents = 0
        docs = []
        tmp_docs = defaultdict(list)
        with open(tsv_file) as tsv_f:
            for line in tsv_f:
                try:
                    doc_id, doc_sent = line.split('\t')
                    tmp_docs[doc_id].append(doc_sent.strip())
                    total_sents += 1
                except BaseException:
                    raise Exception("Unable to read tsv file")

        for doc_id, doc_text in tmp_docs.items():
            docs.append((doc_id, doc_text))
        return docs, total_sents

    def get_docs(self) -> List[Tuple[str, str]]:
        """ returns list of parsed documents
        Returns:
            list(tuple(str, str)): A list of tuples -> (doc_id, doc_text)
        """
        return self.docs

    def log_doc_stats(self):
        """ log statistics of documents"""
        logging.info(
            "Total Document(s): %d, Total Sentence(s): %d",
            self.total_docs,
            self.total_sents)

    def get_queries(self):
        """ returns list of sentences as search queries

        Returns:
           list(tuple(str, str)): list of tuples -> (str, str)
        """
        queries = []
        for doc_id, doc_text in self.docs:
            for i, query in enumerate(doc_text):
                query_id = "%s_%i" % (doc_id, i)
                queries.append((query_id, query))
        return queries
