#!/usr/bin/env bash
#
# Installs ElasticSearch and the dependencies.
# Should be run from project root.

set -e

rootdir=$(cd `dirname $0/`/.. && pwd)
cd $rootdir

# 1. create virtualenv
echo "1. Creating virtualenv: elastic4clir"
virtualenv -p $(which python3) elastic4clir
source elastic4clir/bin/activate
pip install -r requirements.txt
python setup.py install

# 2. download ElasticSearch
version=6.5.3
echo "2. Downloading ElasticSearch"
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-${version}.tar.gz
tar -xf elasticsearch-${version}.tar.gz
rm elasticsearch-${version}.tar.gz

# 3. download and compile trec eval
git clone https://github.com/usnistgov/trec_eval.git
cd trec_eval
make
