#!/usr/bin/env bash

# based on solution of homework 6
# call from 06_project folder

docker-compose --env-file ../.env up -d --build 

# may need to adapt time if images are build for the first time
sleep 60

pipenv run python -m unittest tests/integration_test.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

echo "yay integration tests work!"

docker-compose down