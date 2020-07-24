CREATE EXTENSION multicorn;

CREATE EXTENSION plpythonu;

CREATE OR REPLACE FUNCTION cypher(query text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_default_server(query, '{}'):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_default_server(query, params):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text, server text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_with_server(query, params, server):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text, server text, dbname text) RETURNS SETOF json
LANGUAGE plpython3u
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_with_server(query, params, server, dbname):
    yield result
$$;
