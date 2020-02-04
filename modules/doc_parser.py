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
        doc_file_type (str): type of input file (txt or sgml)
        docs (list(tuple(str, str))): List of tuples -> (doc_id, doc_text)
        total_sents (int): Total number of sentences in documents
    """

    # constants
    SGML = 'sgml'
    TXT = 'txt'

    def __init__(self, doc_file_path: str, doc_mapping_file_path: str = None, doc_length: int = 1):
        """ constructor

        Args:
            doc_file_path (str): path to the document
            doc_mapping_file_path (str): path to an optional mapping file that maps
            every line in doc_file to a doc_id and seg_id
            doc_length (int): specifies the number of sentences per document. 
                              Used only when input doc file is in raw text format and doc_mapping_file is not specified.
        """
        self.doc_file_type = self.get_file_type(doc_file_path)

        try:
            if self.doc_file_type == self.SGML:
                self.docs, self.total_sents = self.parse_sgml(doc_file_path)
            else:
                self.docs, self.total_sents = self.parse_txt(doc_file_path, doc_mapping_file_path, doc_length)
            self.total_docs = len(self.docs)
        except:
            raise Exception("Failed to parse file.")


    def get_file_type(self, file_path: str) -> str:
        """A method used to determine the type of input file

        Note:
            If file does not have an extension, defaults to text

        Args:
            file_path (str): path of a file
        """
        file_ext = path.splitext(file_path)[-1][1:]
        if file_ext.lower() in ['sgm', 'sgml']:
            return self.SGML
        elif file_ext.lower() in ['txt']:
            return self.TXT
        return self.TXT

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
                    doc_text.append((int(sentence.get('id')), sentence.get_text()))

                if doc_text:
                    #sort by segid in ascending order
                    doc_text = sorted(doc_text, key = lambda e: e[0])
                    doc_text = [e[1] for e in doc_text]
                    docs.append((doc_id, doc_text))
        return docs, total_sents

    @staticmethod
    def parse_txt(txt_file: str, doc_mapping_file: str = None, doc_length: int = 1) -> Tuple[List[Tuple[str, str]], int]:
        """ Method used to parse tsv files

        Note:
            TXT file contains one sentence segment every line.

        Args:
            txt_file (str): path to txt file
            doc_mapping_file (str): path to an optional doc_mapping_file
            doc_length (int): Number of sentences per document, used when doc_mapping_file is not specified

        Raises:
            Exception: if unable to read txt file

        Returns:
            tuple(list(tuple(str, str)), int): A list of tuples -> (doc_id, doc_text) and
            total number of sentences
        """
        total_sents = 0
        docs = []
        docs_dict = defaultdict(list)
        doc_texts = []
        doc_ids = [] 

        with open(txt_file) as txt_f:
            for line in txt_f:
                try:
                    doc_sent = line.strip()
                    doc_texts.append(doc_sent)
                    total_sents += 1
                except BaseException:
                    raise Exception("Unable to read txt file")

        if doc_mapping_file is not None:
            with open(doc_mapping_file) as doc_mapping_f:
                for line in doc_mapping_f:
                    try:
                        doc_id, seg_id = line.strip().split('\t')
                        doc_ids.append((doc_id, int(seg_id)))
                    except BaseException:
                        raise Exception("Doc boundary file is not formatted correctly")
        else:
            cur_doc_id = 1
            cur_seg_id = 1
            for i in range(len(doc_texts)):
                doc_ids.append(("S%i"%cur_doc_id, cur_seg_id))
                cur_seg_id += 1
                if (i+1) % doc_length == 0:
                    cur_doc_id +=1
                    cur_seg_id = 1

        #ensure the file lengths match
        if len(doc_texts) != len(doc_ids):
            raise ValueError("Number of lines in %s != Number of lines in %s" % (txt_file, doc_mapping_file))

        for doc_text, (doc_id, doc_segid) in zip(doc_texts, doc_ids):
            docs_dict[doc_id].append((doc_text, doc_segid))

        for doc_id in docs_dict:
            doc_text = [doc_sent for doc_sent, _ in sorted(docs_dict[doc_id], key=lambda e: e[1])]
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

    def get_sentences(self):
        """ returns list of sentences

        Returns:
           list(str): list of sentences
        """
        sentences = []
        for doc_id, doc_text in self.docs:
            for sentence in enumerate(doc_text):
                sentences.append(sentence)
        return sentences

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
