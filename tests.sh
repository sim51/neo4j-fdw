#!/bin/bash


####################################################################
# Before all tests
####################################################################
echo "~~~"
echo "~ Run docker compose"
echo "~~~"
docker-compose pull
docker-compose up --build --detach

echo "~~~"
echo "~ Install/Update extension in Postgres"
echo "~~~"
docker exec -it fdw-pg /source/docker/postgres/init.sh

echo "~~~"
echo "~ Loading Movie database"
echo "~~~"
# Wait until the database is up and ready
echo "~~~"
echo "~ Waiting Neo4j to be ready"
echo "~~~"
until $(curl --output /dev/null --silent --head --fail http://localhost:7474); do
  printf '.'
  sleep 1
done
echo
docker exec -it fdw-neo4j /source/docker/neo4j/init.sh
####################################################################
# Run python unit test
####################################################################
echo "~~~"
echo "~ Running python tests"
echo "~~~"
echo

py.test

RESULT=$?
if [ $RESULT -gt 0 ]; then
  echo "Some python tests failed"
  exit 1
fi

####################################################################
# Running pg_regress tests
####################################################################
echo "~~~"
echo "~ Running pg_regress tests"
echo "~~~"
echo

echo "~ Execute pg_regress tests"
docker exec -it fdw-pg /source/pg_regress.sh /source/test
if [ $? -gt 0 ]; then
  echo "Some regress test failed"
  exit 1
fi

####################################################################
# After all tests
####################################################################
echo "~~~"
echo "~ After all tests"
echo "~~~"
echo

echo "~ Stop docker containers"
docker-compose down
