#!/bin/bash

IS_GPU=$1
DOCKERFILE="server/cpu.Dockerfile"

if [ "${IS_GPU}" = "gpu" ]; then
    echo "Building GPU version"
    DOCKERFILE="server/gpu.Dockerfile"
fi

docker build --target api -t br-api server/ -f ${DOCKERFILE}
docker build --target background -t br-background server/ -f ${DOCKERFILE}
docker build --target ui -t br-ui ui/
