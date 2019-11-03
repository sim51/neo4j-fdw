\a
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS ''The Matrix'' RETURN m ORDER BY id(m) DESC');
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS "The Matrix" RETURN m ORDER BY id(m) DESC');
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS $search RETURN m ORDER BY id(m) DESC','{''search'':''Matrix''}');
SELECT *  FROM cypher('MATCH (m:Movie)  WHERE m.title CONTAINS $search RETURN m ORDER BY id(m) DESC','{"search":"Matrix"}');
SELECT name, born  FROM cypher('MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) WHERE m.title=$movie RETURN p.name AS name, p.born AS born ORDER BY born DESC','{"movie":"The Matrix"}') , json_to_record(cypher) as x(name varchar, born smallint);
select json_object_agg(key,value::jsonb-'id') as result from cypher('create (a:A {name : "test"}),(b:B {name : "thing"}),(c:B {name : "other"}) return *;') c, lateral json_each(c);
select c->'r'->>'type' as rel_type,c->'r'->>'properties' as rel_properties,json_array_length(json_agg(n)) as node_count from cypher('match(a),(b) where a.name = "test" and b.name = "thing" CREATE (a)-[r:RELTYPE {name : "test-thing"}]->(b) return r;') c, lateral json_array_elements(c->'r'->'nodes') n group by 1,2;
select c->'r'->>'type' as rel_type,c->'r'->>'properties' as rel_properties,json_array_length(json_agg(n)) as node_count from cypher('match(a),(b) where a.name = "thing" and b.name = "other" CREATE (a)-[r:RELTYPE {name : "thing-other"}]->(b) return r;') c, lateral json_array_elements(c->'r'->'nodes') n group by 1,2;
select segment->>'type' as rel_type,segment->'properties' as rel_properties from cypher('match p = (a) - [*] -> (b) where a.name = "test" and b.name = "other" return p;') c, lateral json_array_elements(c->'p') segment;
