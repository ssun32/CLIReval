#!/usr/bin/env bash
#
# Convenience script for managing ElasticSearch server

function status_request {
    echo "Current ElasticSearch server status:"
    curl "$1/_cat/indices?v"
}

function start_server {
    echo "Starting ElasticSearch server"
    echo "ES_JAVA_OPTS=\"-Xms${quickstir_es_memory} -Xmx${quickstir_es_memory}\" ./elasticsearch-${version}/bin/elasticsearch -d -Ehttp.port=${quickstir_es_port} -Epath.data=${quickstir_es_store}/data -Epath.logs=${quickstir_es_store}/logs"
    ES_JAVA_OPTS="-Xms${quickstir_es_memory} -Xmx${quickstir_es_memory}" ./elasticsearch-${version}/bin/elasticsearch -d -Ehttp.port=${quickstir_es_port} -Epath.data=${quickstir_es_store}/data -Epath.logs=${quickstir_es_store}/logs
    echo "PID: $(jps | grep Elasticsearch)"
    echo "Make sure server is up by running './scripts/server.sh status' and checking 'health status, etc' info is returned"
}

if [ $# -ne 1 ]; then
    echo "Usage: server.sh command={start,stop,pause,status}"
    echo "  start: start the ElasticSearch server"
    echo "  check-start-wait: see if an ElasticSearch is running: if so, use it; if not, start one and wait until it is responsive"
    echo "  stop:  stop the ElasticSearch server and delete index"
    echo "  pause:  stop the ElasticSearch server and keep index"
    echo "  status: show status of ElasticSearch server"
    exit
fi

# ElasticSearch version
version=6.5.3

# User options: port, java memory, data/log store path
if [ -z $quickstir_es_port ]; then
    export quickstir_es_port=9200
fi

if [ -z $quickstir_es_memory ]; then
    #export quickstir_es_memory=256m
    export quickstir_es_memory=5g
fi

if [ -z $quickstir_es_store ]; then
    export quickstir_es_store=./elasticsearch-${version}/
fi

endpoint="http://localhost:${quickstir_es_port}"

if [ $1 == 'start' ]; then
    start_server

elif [ $1 == 'check-start-wait' ]; then
    echo "Checking if there's an elasticsearch available at: $quickstir_es_port"
    status_request "${endpoint}"
    code=$?
    if [[ "$code" == "0" ]]; then
        echo "Running with specified ES"
    else
        start_server
        echo "Waiting for ES to be online (this can take a while when hosts or disks are busy)"
        sleep 10
        status_request "${endpoint}"
        code=$?
        while [ $code -ne 0 ]; do
            echo "Still waiting on elasticsearch start..."
            sleep 10
            status_request "${endpoint}"
            code=$?
        done
    fi

elif [ $1 == 'stop' ]; then
    es_pid=`jps | grep Elasticsearch | cut -f 1 -d ' '`
    echo "Stopping ElasticSearch server with PID:" $es_pid
    if [ -n "$es_pid" ]; then
        echo "Cleaning ElasticSearch index"
        curl -XDELETE "${endpoint}/*"
        echo
        kill $es_pid
    fi

elif [ $1 == 'pause' ]; then
    es_pid=`jps | grep Elasticsearch | cut -f 1 -d ' '`
    echo "Stopping ElasticSearch server with PID:" $es_pid
    if [ -n "$es_pid" ]; then
        kill $es_pid
    fi

elif [ $1 == 'status' ]; then
    status_request "${endpoint}"

else
    echo "Command unknown."
    echo "Usage: server.sh command={start,stop,status}"
fi
