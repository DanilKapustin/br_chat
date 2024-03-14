#!/bin/bash

DOMAIN=$1

if [ -z "${DOMAIN}" ]; then
    echo "Usage: bin/generate-certs.sh <domain>"
    exit 1
fi

CONFIGS="-f docker/docker-compose.gencert.yml"

docker compose ${CONFIGS} up -d gencert_webserver
docker compose ${CONFIGS} run --rm certbot certonly --webroot --webroot-path /var/www/certbot/ -d "${DOMAIN}"
docker compose ${CONFIGS} stop gencert_webserver
docker compose ${CONFIGS} rm gencert_webserver
