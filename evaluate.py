from modules import search, doc_parser
from bs4 import BeautifulSoup as bs
import argparse
import os
import subprocess
from collections import defaultdict
import logging

if __name__ == '__main__':
    cmdline_parser = argparse.ArgumentParser(description='MT2IR')
    cmdline_parser.add_argument('ref', help='reference file')
    cmdline_parser.add_argument('mt', help='translation file')
    cmdline_parser.add_argument('--port', type=int,
                                default=9200,
                                help='elasticsearch port (default: 9200)')

    args = cmdline_parser.parse_args()
    logging.basicConfig(
                level=os.environ.get("LOGLEVEL", "INFO"),
                format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                )
    logging.info('Loading documents: ref -> %s, mt -> %s' % (args.ref, args.mt))
    ref = doc_parser(args.ref)
    mt = doc_parser(args.mt)

    query_iterable = ref.get_queries()

    es = search(ref.get_docs(), mt.get_docs(), query_iterable, "standard")
    tmp_qrel_f, tmp_res_f = es.get_qrel_and_res_files()
    subprocess.call(["./trec_eval/trec_eval", "-m", "all_trec", "-M1000", tmp_qrel_f.name, tmp_res_f.name])
