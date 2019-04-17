CREATE EXTENSION multicorn;

CREATE EXTENSION plpythonu;

CREATE OR REPLACE FUNCTION cypher(query text) RETURNS SETOF json
LANGUAGE plpythonu
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_default_server(plpy, query, '{}'):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text) RETURNS SETOF json
LANGUAGE plpythonu
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_default_server(plpy, query, params):
    yield result
$$;

CREATE OR REPLACE FUNCTION cypher(query text, params text, server text) RETURNS SETOF json
LANGUAGE plpythonu
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_with_server(plpy, query, params, server):
    yield result
$$;