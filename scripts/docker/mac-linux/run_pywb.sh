#!/bin/bash

container_err=$(docker container inspect pywb 2>&1 1>/dev/null)
if [ -n "$container_err" ]  
then
    docker run -it --name pywb -v ~/Desktop/pywb/data:/app/data pywb
else
    docker start -ia pywb
fi