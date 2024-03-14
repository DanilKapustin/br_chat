#!/bin/bash

CONFIGS="-f docker/docker-compose.yml -f docker/docker-compose.https.yml"

docker compose ${CONFIGS} down
