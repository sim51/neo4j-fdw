# Neo4j Foreign Data Wrapper

## Purpose

Neo4j-fw is a foreign data wrapper for Postgresql. It can be used to access data stored into a Neo4j database from Postgresql.

## Dependencies

You will need the `py2neo` library.

## Connection options

Connection options are
``server``
  The remote host of Neo4j (default is localhost)
``port``
  The remote port of Neo4j (default is 7474)
``user``
  The remote user for Neo4j
``password``
  The remote password for Neo4j
``cypher``
  The cypher query to construct teh virtual table

When defining the table, the local column names will be used to retrieve the remote column data.
Moreover, the local column types will be used to interpret the results in the remote table. 

**NB :** You have name all your

## What does it do to reduce the amount of fetched data ?

- `quals` are pushed to the remote database whenever possible. This include
  simple operators :
    - equality, inequality (=, <>, >, <, <=, >=)
    - like, ilike and their negations

## Usage example

.. code-block:: sql
  CREATE SERVER multicorn_neo4j FOREIGN DATA WRAPPER multicorn
  OPTIONS (
      wrapper  'neo4jfdw.Neo4jForeignDataWrapper',
      server   'localhost',
      port     '7474',
      user     'neo4j',
      password 'admin'
  );
  CREATE FOREIGN TABLE neo4j_trial_synthesis (
    year            integer,
    country         varchar,
    organism        varchar,
    organism_type   varchar,
    variety         varchar,
    product         varchar,
    yield_utc       float8,
    yield_treated   float8,
    yield_diff      float8,
    protein_utc     float8,
    protein_treated float8,
    protein_diff    float8,
    weight_utc      float8,
    weight_treated  float8,
    weight_diff     float8
  ) SERVER multicorn_neo4j OPTIONS (
    cypher 'MATCH
            	(trial:Trial)-[:CONCERNED_PLOT]->(plot:Plot),
            	(trial)-[:IS_TYPE_OF]->(type:TrialType),
            	(trial)-[:CONCERNED_VARIETY]->(variety:Variety),
            	(trial)-[:CONCERNED_PRODUCT]->(product:Product),
            	(trial)-[:IS_LOCALIZED_IN]->(country:Country),
            	(trial)-[:MADE_BY]->(organism:Organism),
                (trial)-[:ON_DATE]->(year:Year)
            RETURN
              year.value AS year,
              country.name AS country,
              organism.name AS organism,
              organism.type AS organism_type,
              variety.name AS variety,
              product.name AS product,
              trial.yield AS yield_utc,
              trial.yieldPa AS yield_treated,
              (trial.yield - trial.yieldPa) AS yield_diff,
              trial.protein AS protein_utc,
              trial.proteinPa AS protein_treated,
              (trial.protein - trial.proteinPa) AS protein_diff,
              trial.weight AS weight_utc,
              trial.weightPa AS weight_treated,
              (trial.weight - trial.weightPa) AS weight_diff'
  );
