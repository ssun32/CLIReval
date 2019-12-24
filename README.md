# Installing MT2IR

Typically, preparing the system involves the following:

1. Install the software dependencies
1. Install elasticsearch
1. Start elasticsearch
1. Run software (experiments, etc.)
1. Stop elasticsearch

## Dependencies
* Python 3.7
* [NumPy](http://www.numpy.org/), tested with 1.15.4
* [Python Elastic Search Client](https://elasticsearch-py.readthedocs.io/en/master/), `pip install elasticsearch`
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), use to parse sgml files (`pip install bs4`)
* [jenkspy 0.1.5](https://github.com/mthh/jenkspy), a fast python implementation of jenks natural breaks algorithm


``` Installation
* Install python dependencies  `pip install -r requirements.txt`
* Install external tools (elasticsearch and trec_eval) `bash scripts/install_external_tools.sh`
```
