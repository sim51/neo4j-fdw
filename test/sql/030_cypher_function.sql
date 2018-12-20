\a
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS ''The Matrix'' RETURN m ORDER BY m.released DESC');
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS "The Matrix" RETURN m ORDER BY m.released DESC');
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS $search RETURN m ORDER BY m.released DESC','{''search'':''Matrix''}');
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS $search RETURN m ORDER BY m.released DESC','{"search":"Matrix"}');
SELECT name, born  FROM cypher('MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) WHERE m.title=$movie RETURN p.name AS name, p.born AS born','{"movie":"The Matrix"}') , json_to_record(cypher) as x(name varchar, born smallint)
