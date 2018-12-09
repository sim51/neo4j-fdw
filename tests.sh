#!/bin/bash


####################################################################
# Before all tests
####################################################################
echo "~~~"
echo "~ Before all tests"
echo "~~~"
echo

echo
echo "~ Run docker compose"
docker-compose rm -f
docker-compose pull
docker-compose up --build --detach
sleep 10

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
