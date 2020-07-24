import unittest
import pytest
import sys
from multicorn import Qual
from neo4jPg import neo4jfdw

class QueryGenerationTest(unittest.TestCase):

    def test_all_movie(self):
        options = {
            'url':'bolt://fdw-neo4j',
            'user':'neo4j',
            'password':'admin',
            'cypher':'MATCH (n:Movie) RETURN n.title as movie'
        };
        columns = ['movie'];
        nfdw = neo4jfdw.Neo4jForeignDataWrapper(options, columns);

        query = nfdw.make_cypher([], columns, None)
        self.assertEqual(
            'MATCH (n:Movie) RETURN n.title as movie',
            query
        )


    def test_movie_by_title(self):
        options = {
            'url':'bolt://fdw-neo4j',
            'user':'neo4j',
            'password':'admin',
            'cypher':'MATCH (n:Movie) RETURN n.title as movie'
        };
        columns = ['movie'];
        nfdw = neo4jfdw.Neo4jForeignDataWrapper(options, columns);

        quals = [Qual('movie', '=', 'The Matrix')];
        query = nfdw.make_cypher(quals, columns, None)
        self.assertEqual(
            'MATCH (n:Movie) WITH n.title as movie WHERE movie=$`movie` RETURN movie',
            query
        )

    def test_query_with_where_clauses_defined_by_user_all(self):
        options = {
            'url':'bolt://fdw-neo4j',
            'user':'neo4j',
            'password':'admin',
            'cypher':'MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) /*WHERE{"actor":"p.name", "movie":"m.title"}*/ WITH p.name AS name, m.title AS title, r /*WHERE{"roles":"r.roles"}*/ RETURN name AS actor, title AS movie, r.roles AS roles'
        }
        columns = ['actor', 'movie'];
        nfdw = neo4jfdw.Neo4jForeignDataWrapper(options, columns);

        quals = [];
        query = nfdw.make_cypher(quals, columns, None)
        self.assertEqual(
            'MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) /*WHERE{"actor":"p.name", "movie":"m.title"}*/ WITH p.name AS name, m.title AS title, r /*WHERE{"roles":"r.roles"}*/ RETURN name AS actor, title AS movie, r.roles AS roles',
            query
        )

    def test_query_with_where_clauses_defined_by_user(self):
        options = {
            'url':'bolt://fdw-neo4j',
            'user':'neo4j',
            'password':'admin',
            'cypher':'MATCH (p:Person)-[:ACTED_IN]->(m:Movie) /*WHERE{"actor":"p.name", "movie":"m.title"}*/ WITH p.name AS name, m.title AS title RETURN name AS actor, title AS movie'
        }
        columns = ['actor', 'movie'];
        nfdw = neo4jfdw.Neo4jForeignDataWrapper(options, columns);

        quals = [Qual('movie', '=', 'The Matrix'), Qual('actor', '=', 'Keanu Reeves')];
        query = nfdw.make_cypher(quals, columns, None)

        self.assertIn(
            query,
            [
                'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)  WHERE p.name=$`actor` AND m.title=$`movie` WITH p.name AS name, m.title AS title RETURN name AS actor, title AS movie',
                'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)  WHERE m.title=$`movie` AND p.name=$`actor` WITH p.name AS name, m.title AS title RETURN name AS actor, title AS movie'
            ]
        )

    def test_query_with_where_clauses_defined_by_user_and_generic(self):
        options = {
            'url':'bolt://fdw-neo4j',
            'user':'neo4j',
            'password':'admin',
            'cypher':'MATCH (p:Person)-[:ACTED_IN]->(m:Movie) /*WHERE{"actor":"p.name"}*/ WITH p.name AS name, m.title AS title RETURN name AS actor, title AS movie'
        }
        columns = ['actor', 'movie'];
        nfdw = neo4jfdw.Neo4jForeignDataWrapper(options, columns);

        quals = [Qual('movie', '=', 'The Matrix'), Qual('actor', '=', 'Keanu Reeves')];
        query = nfdw.make_cypher(quals, columns, None)

        self.assertEqual(
            'MATCH (p:Person)-[:ACTED_IN]->(m:Movie)  WHERE p.name=$`actor` WITH p.name AS name, m.title AS title WITH name AS actor, title AS movie WHERE movie=$`movie` RETURN actor, movie',
            query
        )

    def test_query_with_multiple_where_clauses_defined_by_user(self):
        options = {
            'url':'bolt://fdw-neo4j',
            'user':'neo4j',
            'password':'admin',
            'cypher':'MATCH (p:Person) /*WHERE{"actor":"p.name"}*/ WITH p MATCH (p)-[:ACTED_IN]->(m:Movie) /*WHERE{"movie":"m.title"}*/ RETURN p.name AS actor, m.title AS movie'
        }
        columns = ['actor', 'movie'];
        nfdw = neo4jfdw.Neo4jForeignDataWrapper(options, columns);

        quals = [Qual('movie', '=', 'The Matrix'), Qual('actor', '=', 'Keanu Reeves')];
        query = nfdw.make_cypher(quals, columns, None)

        self.assertEqual(
            'MATCH (p:Person)  WHERE p.name=$`actor` WITH p MATCH (p)-[:ACTED_IN]->(m:Movie)  WHERE m.title=$`movie` RETURN p.name AS actor, m.title AS movie',
            query
        )

if __name__ == '__main__':
    unittest.main()
