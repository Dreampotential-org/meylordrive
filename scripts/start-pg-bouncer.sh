#!/bin/bash

docker-compose -f docker-compose-pg-bouncer.yml down --remove-orphans
docker-compose -f docker-compose-pg-bouncer.yml build
docker-compose -f docker-compose-pg-bouncer.yml up -d

exec "$@"

