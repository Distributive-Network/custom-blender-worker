#!/usr/bin/env bash

pids=()
gotsigchld=false

trap '
	if ! "$gotsigchld"; then
		gotsigchld=true
		((${#pids[@]})) && kill "${pids[@]}" 2> /dev/null
	fi 
' CHLD

PORT="${PORT:-8000}"

uvicorn dcp_custom_blender_worker.main:app --port $PORT & pids+=("$!")
npm run start & pids+=("$!")

set -m 
wait 
set +m
