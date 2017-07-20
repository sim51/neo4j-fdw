#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Neo4j Postgres function
"""

import json
import ast
from neo4j.v1 import GraphDatabase, basic_auth


def cypher(plpy, query, params, url, login, password):
    """
        Make cypher query and return JSON result
    """
    #plpy.info(json.__file__ )
    #plpy.info("Url:" + url + " | login:" + str(login) + " | password:" + str(password))

    driver = GraphDatabase.driver( url, auth=basic_auth(login, password))
    session = driver.session()
    result = session.run(query, ast.literal_eval(params))
    keys = list(result.keys())
    for record in result:
        jsonResult  = "{"
        for key in keys:
            if len(jsonResult) > 1:
                jsonResult += ","
            jsonResult += '"' + key + '":'
            object = record[key]
            if object.__class__.__name__ == "Node":
                jsonResult += node2json(object)
            elif object.__class__.__name__ == "Relationship":
                jsonResult += relation2json(object)
            elif object.__class__.__name__ == "Path":
                jsonResult += path2json(object)
            else:
                jsonResult += json.dumps(object)
        jsonResult += "}"
        yield jsonResult
    session.close()

def cypher_with_server(plpy, query, params, server):
    """
        Make cypher query and return JSON result
    """

    sql = "SELECT unnest(srvoptions) AS conf FROM pg_foreign_server"
    if server:
        sql = "SELECT unnest(srvoptions) AS conf FROM pg_foreign_server WHERE srvname='" + server +"'"

    url = 'bolt://localhost'
    login = None
    password = None

    for row in plpy.cursor(sql):
        if row['conf'].startswith("url="):
            url = row['conf'].split("url=")[1]
        if row['conf'].startswith("user="):
            login = row['conf'].split("user=")[1]
        if row['conf'].startswith("password="):
            password = row['conf'].split("password=")[1]

    for result in cypher(plpy, query, params, url, login, password):
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
    jsonResult += '"id": ' + json.dumps(node.id) + ','
    jsonResult += '"labels": ' + json.dumps(node.labels, default=set_default) + ','
    jsonResult += '"properties": ' + json.dumps(node.properties, default=set_default)
    jsonResult += "}"

    return jsonResult


def relation2json(rel):
    """
        Convert a relation to json
    """
    jsonResult = "{"
    jsonResult += '"id": ' + json.dumps(rel.id) + ','
    jsonResult += '"type": ' + json.dumps(rel.type) + ','
    jsonResult += '"properties": ' + json.dumps(rel.properties, default=set_default)
    jsonResult += "}"

    return jsonResult

def path2json(path):
    """
        Convert a path to json
    """
    jsonResult = "["
    if segment.start() is not None:
        jsonResult += node2json(segment.start())

    for segment in path:
        jsonResult += "," + relation2json( segment.relationship() )
        jsonResult += "," + node2json( segment.end() )

    jsonResult += "]"

    return jsonResult

def set_default(obj):
    """
        For JSON Serializer : convert set to list
    """
    if isinstance(obj, set):
        return list(obj)
    raise TypeError
