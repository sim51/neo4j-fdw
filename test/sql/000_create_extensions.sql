\a
CREATE EXTENSION plpython3u;

CREATE EXTENSION multicorn;

CREATE SERVER multicorn_neo4j FOREIGN DATA WRAPPER multicorn
OPTIONS (
    wrapper  'neo4jPg.neo4jfdw.Neo4jForeignDataWrapper',
    url      'bolt://neo4j:7687',
    user     'neo4j',
    password 'admin'
);

CREATE OR REPLACE FUNCTION cypher(query text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_default_server(plpy, query, '{}'):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_default_server(plpy, query, params):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text, server text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_with_server(plpy, query, params, server):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text, server text, dbname text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_with_server(plpy, query, params, server, dbname):
    yield result
$$;