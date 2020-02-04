
# CLIReval


CLIReval is an open-source toolkit that evaluates the quality of MT outputs in the context of a CLIR system, without the need for any actual CLIR dataset. The only inputs required to the tool are the translations and the references. The tool will create a synthetic CLIR dataset, index the translations as documents, and report metrics such as mean average precision.

## Dependencies
* Python 3.7
* [NumPy](http://www.numpy.org/), tested with 1.15.4
* [Python Elastic Search Client](https://elasticsearch-py.readthedocs.io/en/master/), `pip install elasticsearch`
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), use to parse sgml files (`pip install bs4`)
* [jenkspy 0.1.5](https://github.com/mthh/jenkspy), a fast python implementation of jenks natural breaks algorithm

## Usage
```
usage: evaluate.py [-h] 
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
                   ref mt
```             

|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Options&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Default|Description|
|:--:|:-------------:|:-----|
| ref|  | A file containing reference sentences/documents. |
| mt |  | A file containing translated sentences/documents. |
| \-\-port | 9200 |The Elasticsearch port number of a running Elasticsearch instance.|
| \-\-query_mode | sentences | {sentences,unique_terms}|
| \-\-relv_mode | jenks | {jenks,percentile,query_in_document}|
| \-\-jenks_nb_class | 5 |Number of classes when using `jenks` mode for relevance label converter. |
| \-\-n_percentile | 25 |The threshold percentile when using `percentile` mode for relevance label convertor. Only documents with BM25 scores in the top n_percentile are considered relevant documents. |
| \-\-n_ret | 100 | Maximum number of documents to be returned by Elasticsearch. |
| \-\-qrel_save_path | None | When specified, CLIReval will save trec_eval's query relevance judgments (qrel) file to `qrel_save_path`.  |
| \-\-res_save_path | None | When specified, CLIReval will save trec_eval's results (res) file to `res_save_path`.|
| \-\-target_langcode| en | Language code of the target sentences/documents. CLIReval has built-in analyzers for the following language codes: ar, bg, bn, ca, cs, da, de, el, en, es, eu, fa, fi, fr, ga, gl, hi, hu, hy, id, it, ja, ko, lt, lv, nl, no, pl, pt, ro, ru, sv, th, tr, uk, zh. It will use `standard` analyzer for language codes not in the list.|
| \-\-output_format | json | json or csv.|
| \-\-output_file | None | By default, CLIReval writes output to STDOUT. If \-\-output_file is specified, CLIReval will output to file instead. |
### Starting and stopping Elasticsearch
We provide a convenient script that starts an Elasticsearch instance on port 9200 and set Java heap size to 5GB:
`./scripts/server.sh [start | stop]`

### Run evaluation
python evaluate.py examples/en-de.ref.sgm examples/en-de.mt.sgm

We provide a sample bash script for the pipeline in `example/evaluate.sh` and sample output in 
`example/output.txt`. 

Please refer to [trec_eval documentation](https://w-nlpir.nist.gov/projects/trecvid/trecvid.tools/trec_eval_video/A.README) for an explanation of the output.

## Installation
* Install python dependencies  `pip install -r requirements.txt`
* Install external tools (elasticsearch and trec_eval) `bash scripts/install_external_tools.sh`
