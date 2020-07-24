#!/bin/bash

VERSION=$(su neo4j -s /bin/bash -c "bin/neo4j version")
echo "Neo4j version is $VERSION"

PARSING=( ${VERSION//./ } )
MAJOR=${PARSING[1]}

if [ $((MAJOR)) -lt 4 ]; then
  # Load the data with the cypher shell
  echo "~~~"
  echo "~ Init database"
  echo "~~~"
  su neo4j -s /bin/bash -c "bin/cypher-shell -u neo4j -p admin < /source/scripts/docker/neo4j/initdb.gql"
else
  echo "~~~"
  echo "~ Create dbtest"
  echo "~~~"
  su neo4j -s /bin/bash -c "bin/cypher-shell -u neo4j -p admin -d system 'CREATE DATABASE testdb IF NOT EXISTS;'"
  echo "~~~"
  echo "~ Init database dbtest"
  echo "~~~"
  su neo4j -s /bin/bash -c "bin/cypher-shell -u neo4j -p admin -d testdb < /source/scripts/docker/neo4j/initdb.gql"
fi
