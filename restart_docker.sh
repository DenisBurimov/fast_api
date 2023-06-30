#!/bin/bash
git pull
docker-compose build
if [ $? -eq 0 ]
then
    docker-compose down
    docker-compose up -d
    if [ $? -eq 0]
    then
        echo "Containers have been started successfully"
    else
        echo Exit code: $?
else
    echo Build failed
