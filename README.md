"""
Purpose
-------
Neo4j-fw is a foreign data wrapper for Postgresql. It can be used to access data stored into a Neo4j database from Postgresql

Dependencies
------------
You will need the `py2neo`_ library.

Connection options
~~~~~~~~~~~~~~~~~~
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

When defining the table, the local column names will be used to retrieve the
remote column data.

Moreover, the local column types will be used to interpret the results in the remote table. 

What does it do to reduce the amount of fetched data ?
------------------------------------------------------
- `quals` are pushed to the remote database whenever possible. This include
  simple operators :
    - equality, inequality (=, <>, >, <, <=, >=)
    - like, ilike and their negations
    - IN clauses with scalars, = ANY (array)
    - NOT IN clauses, != ALL (array)
- the set of needed columns is pushed to the remote base, and only those columns will be fetched.

Usage example
-------------

.. code-block:: sql
  CREATE SERVER multicorn_neo4j FOREIGN DATA WRAPPER multicorn
  OPTIONS (
      wrapper  'neo4jfdw.Neo4jForeignDataWrapper',
      server   'localhost',
      port     '7474',
      user     'neo4j',
      password 'admin'
  );
  CREATE FOREIGN TABLE neo4j_movie (
    movie varchar
  ) SERVER multicorn_neo4j OPTIONS (
    cypher 'MATCH (n:Movie) RETURN n.title as movie'
  );
