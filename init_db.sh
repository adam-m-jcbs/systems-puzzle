#!/usr/bin/env bash

docker-compose up -d db
wait
sleep 10 #Hacky way of giving the db enough time to get up and running. 
        #`wait` alone isn't sufficient.
docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"
