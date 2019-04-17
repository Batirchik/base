#!/bin/bash

USER="test"
PASS="test"
SERVICE_ENDPOINT="10.0.0.255:9999"

while true; do
curl http://$SERVICE_ENDPOINT/apitoken?user=$USER&pass=$PASS > api_token
API_TOKEN=`cat api_token`
curl http://$SERVICE_ENDPOINT/task?api_token=$API_TOKEN > task_exists_response
grep 404 task_exists_response && curl http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN > task_run_response
grep "Not found" task_exists_response && curl http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN > task_run_response
grep 200 task_run_response && sleep 60
grep "RESULT" task_run_response && sleep 60
grep 500 task_run_response && curl http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN > task_run_response
grep "ERROR" task_run_response && curl http://$SERVICE_ENDPOINT/task/start?api_token=$API_TOKEN > task_run_response
done