
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
usage: evaluate.py [-h] [--port PORT] [--query_mode {sentences,unique_terms}]
                   [--relv_mode {jenks,percentile,query_in_document}]
                   [--jenks_nb_class JENKS_NB_CLASS]
                     [--n_percentile N_PERCENTILE] [--n_ret N_RET]
                   [--qrel_save_path QREL_SAVE_PATH]
                   [--res_save_path RES_SAVE_PATH]
                   [--output_format {tsv,json}]
                    [--target_langcode {language code}]
                   [--output_file OUTPUT_FILE]
                   ref mt
```             

| Option|Default| Description|
| :-------------: |:-------------:| :-----:|
| ref|  | reference file |
| mt |  | translation file |
| --port | 9200|elasticsearch port (default: 9200)|


### Start and Stop ElasticSearch
`./scripts/server.sh [start | stop]`

### Run evaluation
python evaluate.py example/en-de.ref.sgm example/en-de.mt.sgm --target_langcode de --port 9200

We provide a sample bash script for the pipeline in `example/evaluate.sh` and sample output in 
`example/output.txt`. 

Please refer to [trec_eval documentation](https://w-nlpir.nist.gov/projects/trecvid/trecvid.tools/trec_eval_video/A.README) for an explanation of the output.

## Installation
* Install python dependencies  `pip install -r requirements.txt`
* Install external tools (elasticsearch and trec_eval) `bash scripts/install_external_tools.sh`
