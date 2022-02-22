#! /bin/bash

http_response_get(){
    status_code=$(curl --write-out %{http_code} --silent --output /dev/null $1)
    echo "Site $1 status response is $status_code"
    if [ "$status_code" -eq 403 ] || [ "$status_code" -eq 404 ] || [ "$status_code" -eq 500 ] || [ "$status_code" -eq 503 ] || [ "$status_code" -eq 504 ] ; then
        exit 1
    fi
}

http_response_post(){
    status_code=$(curl -X POST -H "Content-type: application/json" -d $1 $2 --write-out %{http_code}    --silent --output /dev/null)
    echo "Site $2 status response is $status_code"
    if [ "$status_code" -eq 403 ] || [ "$status_code" -eq 404 ] || [ "$status_code" -eq 500 ] || [ "$status_code" -eq 503 ] || [ "$status_code" -eq 504 ] ; then
        exit 1
    fi
}

sleep 30

http_response_get http://localhost:5001/init
http_response_get http://localhost:5001/txt2patterns
http_response_get http://localhost:5001/patterns
http_response_post '{ "pattern": "Cancer de piel", "db": "PUBMED", "description": "Cancer muy comun"}' http://localhost:5001/pattern2mysql

exit 0
