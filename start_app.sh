#!/usr/bin/env bash

docker-compose up -d db
wait
sleep 5
docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"
wait
sleep 5
docker-compose up -d
