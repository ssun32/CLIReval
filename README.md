
# CLIReval


CLIReval is an open-source toolkit that evaluates the quality of MT outputs in the context of a CLIR system, without the need for any actual CLIR dataset. The only inputs required to the tool are the translations and the references. The tool will create a synthetic CLIR dataset, index the translations as documents, and report metrics such as mean average precision.

## Dependencies
* Python 3.7
* [NumPy](http://www.numpy.org/), tested with 1.15.4
* [Python Elastic Search Client](https://elasticsearch-py.readthedocs.io/en/master/), `pip install elasticsearch`
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), use to parse sgml files (`pip install bs4`)
* [jenkspy 0.1.5](https://github.com/mthh/jenkspy), a fast python implementation of Jenks natural breaks algorithm (`pip install jenkspy`)

## Usage
```
usage: evaluate.py [-h] 
				   [--doc_mapping_file DOC_MAPPING_FILE]
				   [--doc_length DOC_LENGTH]
				   [--port PORT] 
				   [--query_mode {sentences,unique_terms}]
                   [--relv_mode {jenks,percentile,query_in_document}]
                   [--jenks_nb_class JENKS_NB_CLASS]
                   [--n_percentile N_PERCENTILE] 
                   [--n_ret N_RET]
                   [--qrel_save_path QREL_SAVE_PATH]
                   [--res_save_path RES_SAVE_PATH]
                   [--target_langcode]
                   [--output_format {tsv,json}]
                   [--output_file OUTPUT_FILE]
                   ref_file mt_file
```             

|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Option&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Default|Description|
|:--:|:-------------:|:-----|
| ref_file|  | A file containing reference sentences/documents. |
| mt_file |  | A file containing translated sentences/documents. |
| \-\-doc_mapping_file | None | A TSV file which maps sentences in ref_file and mt_file to doc_ids and seg_ids. |
| \-\-doc_length | 1 | When document boundary is not defined, use this argument to specific the number of sentences in every document. This argument will only be used when input files are raw text files and \-\-doc_mapping_file is not specified. |
| \-\-port | 9200 |The Elasticsearch port number of a running Elasticsearch instance.|
| \-\-query_mode | sentences | {sentences,unique_terms}|
| \-\-relv_mode | jenks | {jenks,percentile,query_in_document}|
| \-\-jenks_nb_class | 5 |Number of classes when using `jenks` mode for relevance label converter. |
| \-\-n_percentile | 25 |The threshold percentile when using `percentile` mode for relevance label convertor. Only documents with BM25 scores in the top n_percentile are considered relevant documents. |
| \-\-n_ret | 100 | Maximum number of documents to be returned by Elasticsearch. |
| \-\-qrel_save_path | None | When specified, CLIReval will save trec_eval's query relevance judgments (qrel) file to `qrel_save_path`.  |
| \-\-res_save_path | None | When specified, CLIReval will save trec_eval's results (res) file to `res_save_path`.|
| \-\-target_langcode| en | Language code of the target sentences/documents. CLIReval has built-in analyzers for the following language codes: ar, bg, bn, ca, cs, da, de, el, en, es, eu, fa, fi, fr, ga, gl, hi, hu, hy, id, it, ja, ko, lt, lv, nl, no, pl, pt, ro, ru, sv, th, tr, uk, zh. CLIReval will use `standard` analyzer for language codes not in the list.|
| \-\-output_format | json | json or csv.|
| \-\-output_file | None | By default, CLIReval writes output to STDOUT. If \-\-output_file is specified, CLIReval will output to file instead. |
### Starting and stopping Elasticsearch
We provide a convenient script that starts an Elasticsearch instance on port 9200 and set Java heap size to 5GB:
`./scripts/server.sh [start | stop]`

### Example runs
Evaluating with defined document boundaries:
* `python evaluate.py examples/en-de.ref.sgm examples/en-de.mt.sgm`
* `python evaluate.py examples/en-de.ref.txt examples/en-de.mt.txt  --doc_mapping_file examples/en-de.doc_mappings.tsv`
Evaluating with artificial document boundary:
*`python evaluate.py examples/en-de.ref.txt examples/en-de.mt.txt --doc_length 10` (1 sentence per document)
*`python evaluate.py examples/en-de.ref.txt examples/en-de.mt.txt --doc_length 10` (10 sentence per documents)

We also provide a sample bash script `example/evaluate.sh` which runs the entire pipeline: 1) start an Elasticsearch instance, 2) run evaluation 3) shut down Elasticsearch.
A sample output in `example/output.txt`. 

Please refer to [trec_eval documentation](https://w-nlpir.nist.gov/projects/trecvid/trecvid.tools/trec_eval_video/A.README) for explanation of the output.

## Installation
* Install python dependencies  `pip install -r requirements.txt`
* Install external tools (elasticsearch and trec_eval) `bash scripts/install_external_tools.sh`
