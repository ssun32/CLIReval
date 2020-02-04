import os
import unittest
from collections import defaultdict
from context import modules


class TestDocParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.sgm_doc_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'test_data/test.sgm')
        cls.tsv_doc_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'test_data/test.tsv')
        cls.txt_doc_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'test_data/test.txt')
        cls.txt_doc_mapping_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'test_data/test.doc_mapping.tsv')

        cls.docs = defaultdict(list)
        cls.sents = []
        with open(cls.tsv_doc_path) as tsv_f:
            for line in tsv_f:
                doc_id, doc_sent = line.strip().split('\t')
                cls.docs[doc_id].append(doc_sent)
                cls.sents.append(doc_sent)

        cls.total_sents = sum([len(doc) for doc in cls.docs.values()])
        cls.total_docs = len(cls.docs.keys())

    def test_init(self):
        """Test __init__ function of DocParser"""
        sgm_doc_parser = modules.DocParser(self.sgm_doc_path)
        txt_doc_parser = modules.DocParser(self.txt_doc_path, self.txt_doc_mapping_path)
        txt_doc_parser2 = modules.DocParser(self.txt_doc_path, doc_length=2)

        with self.assertRaises(Exception):
            bad_doc_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                'test_data/this_file_does_not_exists')
            modules.DocParser(bad_doc_path)

        self.assertEqual(sgm_doc_parser.total_docs, self.total_docs)
        self.assertEqual(sgm_doc_parser.total_sents, self.total_sents)

        self.assertEqual(txt_doc_parser.total_docs, self.total_docs)
        self.assertEqual(txt_doc_parser.total_sents, self.total_sents)
        self.assertEqual(txt_doc_parser2.total_docs, self.total_sents/2)
        self.assertEqual(txt_doc_parser2.total_sents, self.total_sents)

    def test_get_file_type(self):
        """Test whether it is getting correct file_type"""
        doc_parser = modules.DocParser(self.sgm_doc_path)

        self.assertEqual(doc_parser.get_file_type(self.sgm_doc_path), 'sgml')
        self.assertEqual(doc_parser.get_file_type(self.txt_doc_path), 'txt')

    def test_parse_sgml(self):
        """Test sgml parser"""
        docs, total_sents = modules.DocParser.parse_sgml(self.sgm_doc_path)

        self.assertEqual(self.total_sents, total_sents)
        for doc_id, doc in docs:
            self.assertEqual("\n".join(self.docs[doc_id]), "\n".join(doc))

    def test_parse_txt(self):
        """Test txt parser"""
        docs, total_sents = modules.DocParser.parse_txt(self.txt_doc_path, self.txt_doc_mapping_path)
        self.assertEqual(self.total_sents, total_sents)
        for doc_id, doc in docs:
            self.assertEqual("\n".join(self.docs[doc_id]), "\n".join(doc))

        docs, total_sents = modules.DocParser.parse_txt(self.txt_doc_path, doc_length=1)
        for sentence, (doc_id, doc) in zip(self.sents, docs):
            self.assertEqual(sentence, "\n".join(doc))

    def test_get_docs(self):
        """Test get docs"""
        docs = modules.DocParser(self.sgm_doc_path).get_docs()
        for doc_id, doc in docs:
            self.assertEqual("\n".join(self.docs[doc_id]), "\n".join(doc))

    def test_get_queries(self):
        """Test get queries"""
        queries = modules.DocParser(self.sgm_doc_path).get_queries()
        for doc_id in self.docs:
            for i, sent in enumerate(self.docs[doc_id]):
                self.assertIn(("%s_%d" % (doc_id, i), sent), queries)
