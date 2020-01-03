# MT2IR (TO-DO)

Typically, preparing the system involves the following:

1. Install the software dependencies
1. Install elasticsearch and trec_eval
1. Start elasticsearch
1. Run experiments
1. Stop elasticsearch

## Dependencies
* Python 3.7
* [NumPy](http://www.numpy.org/), tested with 1.15.4
* [Python Elastic Search Client](https://elasticsearch-py.readthedocs.io/en/master/), `pip install elasticsearch`
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), use to parse sgml files (`pip install bs4`)
* [jenkspy 0.1.5](https://github.com/mthh/jenkspy), a fast python implementation of jenks natural breaks algorithm

## Usage
```python
usage: evaluate.py [-h] [--port PORT] [--query_mode {sentences,unique_terms}]
                   [--relv_mode {jenks,percentile,query_in_document}]
                   [--jenks_nb_class JENKS_NB_CLASS]
                   [--n_percentile N_PERCENTILE] [--n_ret N_RET]
                   [--qrel_save_path QREL_SAVE_PATH]
                   [--res_save_path RES_SAVE_PATH]
                   [--output_format {tsv,json}]
                   [--analyzer {arabic,armenian,basque,bengali,brazilian,bulgarian,catalan,cjk,czech,danish,dutch,english,finnish,french,galician,german,greek,hindi,hungarian,indonesian,irish,italian,latvian,lithuanian,norwegian,persian,portuguese,romanian,russian,sorani,spanish,swedish,turkish,thai}]
                   [--output_file OUTPUT_FILE]
                   ref mt
```             

| Option|Default| Description|
| :-------------: |:-------------:| :-----:|
| ref|  | reference file |
| mt |  | translation file |
| --port | 9200|elasticsearch port (default: 9200)'|

## Installation
* Install python dependencies  `pip install -r requirements.txt`
* Install external tools (elasticsearch and trec_eval) `bash scripts/install_external_tools.sh`

## Start and Stop ElasticSearch
`./scripts/server.sh [start | stop]`

## Run evaluation
python evaluate.py sample/en-de.ref.sgm sample/en-de.mt.sgm
