#!/bin/bash

# Load the data with the cypher shell
echo "~~~"
echo "~ Init database"
echo "~~~"
su neo4j -s /bin/bash -c "bin/cypher-shell -u neo4j -p admin < /source/scripts/docker/neo4j/initdb-legacy.gql"
