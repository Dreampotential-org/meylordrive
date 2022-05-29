#!/bin/bash

docker-compose -f docker-compose-postgres.yml down --remove-orphans
docker-compose -f docker-compose-postgres.yml build
docker-compose -f docker-compose-postgres.yml up -d

exec "$@"

