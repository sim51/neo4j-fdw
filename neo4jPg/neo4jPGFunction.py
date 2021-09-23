from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import CypherSyntaxError, CypherTypeError
import json
import ast
import re
import warnings
from neo4j.meta import ExperimentalWarning

warnings.filterwarnings("ignore", category=ExperimentalWarning)

"""
Neo4j Postgres function
"""


def cypher(plpy, query, params, url, dbname, login, password):
    """
        Make cypher query and return JSON result
    """
    driver = GraphDatabase.driver(url, auth=(login, password))

    # Execute & retrieve neo4j data
    if driver.supports_multi_db():
        session = driver.session(database=(dbname or 'neo4j'))
    else:
        session = driver.session()

    plpy.debug("Cypher function with query " +
               query + " and params " + str(params))

    # Execute & retrieve neo4j data
    try:
        for record in session.run(query, ast.literal_eval(params)):
            jsonResult = "{"
            for key in record.keys():
                if len(jsonResult) > 1:
                    jsonResult += ","
                jsonResult += '"' + key + '":'
                object = record[key]
                if object.__class__.__name__ == "Node":
                    jsonResult += node2json(object)

                # In 1.6 series of neo4j python driver a change to way relationship types are
                # constructed which means ABCMeta is __class__ and the mro needs to be checked
                elif any(c.__name__ == 'Relationship' for c in object.__class__.__mro__):
                    jsonResult += relation2json(object)
                elif object.__class__.__name__ == "Relationship":
                    jsonResult += relation2json(object)

                elif object.__class__.__name__ == "Path":
                    jsonResult += path2json(object)
                else:
                    jsonResult += json.dumps(object)
            jsonResult += "}"
            yield jsonResult
    except CypherSyntaxError as ce:
        raise RuntimeError(
            "Bad cypher query: %s - Error message: %s" % (query, str(ce)))
    except CypherTypeError as ce:
        raise RuntimeError(
            "Bad cypher type in query: %s - Error message: %s" % (query, str(ce)))
    finally:
        session.close()


def cypher_with_server(plpy, query, params, server, dbname="neo4j"):
    """
        Make cypher query and return JSON result
    """
    sql = "SELECT unnest(srvoptions) AS conf FROM pg_foreign_server"
    if server:
        sql = "SELECT unnest(srvoptions) AS conf FROM pg_foreign_server WHERE srvname='" + server + "'"

    url = 'neo4j://localhost'
    login = None
    password = None

    for row in plpy.cursor(sql):
        if row['conf'].startswith("url="):
            url = row['conf'].split("url=")[1]
        if row['conf'].startswith("user="):
            login = row['conf'].split("user=")[1]
        if row['conf'].startswith("password="):
            password = row['conf'].split("password=")[1]

    for result in cypher(plpy, query, params, url, dbname, login, password):
        yield result


def cypher_default_server(plpy, query, params):
    """
        Make cypher query and return JSON result
    """
    for result in cypher_with_server(plpy, query, params, None):
        yield result


def node2json(node):
    """
        Convert a node to json
    """
    jsonResult = "{"
    jsonResult += '"id": ' + json.dumps(node._id) + ','
    jsonResult += '"labels": ' + \
        json.dumps(node._labels, default=set_default) + ','
    jsonResult += '"properties": ' + \
        json.dumps(node._properties, default=set_default)
    jsonResult += "}"

    return jsonResult


def relation2json(rel):
    """
        Convert a relation to json
    """
    jsonResult = "{"
    jsonResult += '"id": ' + json.dumps(rel._id) + ','

    jsonResult += '"type": ' + json.dumps(rel.type) + ','
    jsonResult += '"nodes": [' + \
        node2json(rel.nodes[0]) + ',' + node2json(rel.nodes[1]) + '],'

    jsonResult += '"properties": ' + \
        json.dumps(rel._properties, default=set_default)
    jsonResult += "}"

    return jsonResult


def path2json(path):
    """
        Convert a path to json
    """
    jsonResult = "["

    jsonResult += ",".join([relation2json(segment) for segment in path])

    jsonResult += "]"

    return jsonResult


def set_default(obj):
    """
        For JSON Serializer : convert set to list
    """
    if isinstance(obj, frozenset) or isinstance(obj, set):
        return list(obj)
    raise TypeError
