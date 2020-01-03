#!/usr/bin/env bash
#
# Convenience script for managing ElasticSearch server

function status_request {
    echo "Current ElasticSearch server status:"
    curl "$1/_cat/indices?v"
}

function start_server {
    echo "Starting ElasticSearch server"
    ES_JAVA_OPTS="-Xms${es_memory} -Xmx${es_memory}" ./external_tools/elasticsearch-${version}/bin/elasticsearch -d -Ehttp.port=${es_port}
    #echo "PID: $(jps | grep Elasticsearch)"
    #echo "Make sure server is up by running './scripts/server.sh status' and checking 'health status, etc' info is returned"
}

if [ $# -ne 1 ]; then
    echo "Usage: server.sh command={start,check-start-wait,stop,pause,status}"
    echo "  start: start the ElasticSearch server"
    echo "  check-start-wait: see if an ElasticSearch is running: if so, use it; if not, start one and wait until it is responsive"
    echo "  stop:  stop the ElasticSearch server and delete index"
    echo "  pause:  stop the ElasticSearch server and keep index"
    echo "  status: show status of ElasticSearch server"
    exit
fi

# ElasticSearch version
version=6.5.3
es_port=9200
es_memory=5g

endpoint="http://localhost:${es_port}"

if [ $1 == 'start' ]; then
    start_server

elif [ $1 == 'check-start-wait' ]; then
    echo "Checking if there's an elasticsearch available at: $es_port"
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
