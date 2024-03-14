#!/bin/bash

IS_GPU=$1
CONFIGS="-f docker/docker-compose.yml -f docker/docker-compose.http.yml"

if [ "${IS_GPU}" = "gpu" ]; then
    echo "Running GPU version"
    CONFIGS="${CONFIGS} -f docker/docker-compose.gpu.yml"
fi

docker compose ${CONFIGS} up -d
