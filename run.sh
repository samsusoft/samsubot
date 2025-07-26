# run.sh
#!/bin/bash

ENV=$1

if [ "$ENV" == "dev" ]; then
  docker compose -f docker-compose.dev.yml up --build
elif [ "$ENV" == "test" ]; then
  docker compose -f docker-compose.test.yml up --build
elif [ "$ENV" == "prod" ]; then
  docker compose -f docker-compose.prod.yml up --build
else
  echo "Usage: ./run.sh [dev|test|prod]"
fi