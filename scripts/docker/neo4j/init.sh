#!/bin/bash

# Load the data with the cypher shell
echo "~~~"
echo "~ Init database"
echo "~~~"
bin/neo4j start && sleep 10 && bin/cypher-shell -u neo4j -p neo4j < /source/scripts/docker/neo4j/initdb.gql
