FROM neo4j:3.5-enterprise AS fdwNeo4j

ENV NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
ENV EXTENSION_SCRIPT=/source/docker/neo4j/init.sh

RUN apk add --no-cache curl
