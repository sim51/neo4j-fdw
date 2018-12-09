#!/bin/bash
echo "~~~"
echo "~ Changing password"
echo "~~~"
su-exec neo4j bin/neo4j-admin set-initial-password admin

echo "~~~"
echo "~ Starting Neo4j"
echo "~~~"
su-exec neo4j bin/neo4j start

# Wait until the database is up and ready
echo "~~~"
echo "~ Waiting Neo4j to be ready"
echo "~~~"
until $(curl --output /dev/null --silent --head --fail http://localhost:7474); do
  printf '.'
  sleep 1
done
echo

# Load the data with the cypher shell
echo "~~~"
echo "~ Init database"
echo "~~~"
su-exec neo4j bin/cypher-shell -u neo4j -p admin < /source/docker/neo4j/initdb.gql

tail -f logs/*

echo "~~~"
echo "~ Stopping Neo4j"
echo "~~~"
su-exec neo4j bin/neo4j stop
