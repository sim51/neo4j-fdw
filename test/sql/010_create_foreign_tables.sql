\a
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
    database 'testdb',
    cypher 'MATCH (n:Person) RETURN id(n) AS id, n.name AS name, n.born AS born'
  );

CREATE FOREIGN TABLE actedIn (
    id bigint NOT NULL,
    movie_id bigint NOT NULL,
    person_id bigint NOT NULL
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN id(r) AS id, id(p) AS person_id, id(m) AS movie_id ORDER BY id DESC'
  );

CREATE FOREIGN TABLE actedInWithCustomWhere1 (
    actor varchar NOT NULL,
    movie varchar NOT NULL
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie) /*WHERE{"actor":"p.name", "movie":"m.title"}*/ WITH p.name AS name, m.title AS title, id(m) AS id ORDER BY id DESC RETURN name AS actor, title AS movie'
  );

CREATE FOREIGN TABLE actedInWithCustomWhere2 (
    actor varchar NOT NULL,
    movie varchar NOT NULL
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (p:Person)-[:ACTED_IN]->(m:Movie) /*WHERE{"actor":"p.name"}*/ WITH p.name AS name, m.title AS title, id(m) AS id ORDER BY id DESC RETURN name AS actor, title AS movie'
  );

CREATE FOREIGN TABLE actedInWithCustomWheres (
    actor varchar NOT NULL,
    movie varchar NOT NULL
  ) SERVER multicorn_neo4j OPTIONS (
    database 'testdb',
    cypher 'MATCH (p:Person) /*WHERE{"actor":"p.name"}*/ WITH p MATCH (p)-[:ACTED_IN]->(m:Movie) /*WHERE{"movie":"m.title"}*/ WITH p, m ORDER BY id(m) DESC RETURN p.name AS actor, m.title AS movie'
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
