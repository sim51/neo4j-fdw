#!/bin/bash

# Load the data with the cypher shell
echo "~~~"
echo "~ Init database"
echo "~~~"
su-exec neo4j bin/cypher-shell -u neo4j -p admin < /source/docker/neo4j/initdb.gql
