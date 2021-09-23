CREATE EXTENSION multicorn;
CREATE SERVER multicorn_neo4j FOREIGN DATA WRAPPER multicorn
  OPTIONS (
      wrapper  'neo4jPg.neo4jfdw.Neo4jForeignDataWrapper',
      url      'neo4j://neo4j:7687',
      user     'neo4j',
      password 'admin'
  );
CREATE FOREIGN TABLE movie (
    id bigint NOT NULL,
    title varchar NOT NULL,
    released smallint,
    tagline varchar
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (n:Movie) RETURN id(n) AS id, n.title AS title, n.released AS released, n.tagline AS tagline'
  );
CREATE FOREIGN TABLE person (
    id bigint NOT NULL,
    name varchar NOT NULL,
    born smallint
  ) SERVER multicorn_neo4j OPTIONS (
    cypher 'MATCH (n:Person) RETURN id(n) AS id, n.name AS name, n.born AS born'
  );
CREATE FOREIGN TABLE actedIn (
    id bigint NOT NULL,
    movie_id bigint NOT NULL,
    person_id bigint NOT NULL
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN id(r) AS id, id(p) AS person_id, id(m) AS movie_id'
  );

CREATE FOREIGN TABLE temporal (
  my_date DATE,
  my_localtime TIME,
  my_time TIME WITH TIME ZONE,
  my_datetime TIMESTAMP WITH TIME ZONE,
  my_localdatetime TIMESTAMP,
  my_duration INTERVAL
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (n:TemporalNode) RETURN n.date AS my_date, n.time AS my_time, n.localtime AS my_localtime, n.datetime AS my_datetime, n.localdatetime AS my_localdatetime, n.duration AS my_duration'
  );

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
CREATE OR REPLACE FUNCTION cypher(query text, params text, server text, dbname text) RETURNS SETOF json
LANGUAGE plpythonu
AS $$
from neo4jPg import neo4jPGFunction
for result in neo4jPGFunction.cypher_with_server(plpy, query, params, server, dbname):
    yield result
$$;
