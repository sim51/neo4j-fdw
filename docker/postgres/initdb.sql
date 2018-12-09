
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_neo4j FOREIGN DATA WRAPPER multicorn
  OPTIONS (
      wrapper  'neo4jPg.neo4jfdw.Neo4jForeignDataWrapper',
      url      'bolt://neo4j:7687',
      user     'neo4j',
      password 'admin'
  );

CREATE FOREIGN TABLE movie (
    id bigint NOT NULL,
    title varchar NOT NULL,
    released smallint,
    tagline varchar
  ) SERVER multicorn_neo4j OPTIONS (
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
    cypher 'MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN id(r) AS id, id(p) AS person_id, id(m) AS movie_id'
  );
