#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Neo4j Postgres function
"""

import json
from py2neo import neo4j


def cypher(plpy, query, server, port, login, password):
    """
        Make cypher query and return JSON result
    """
    plpy.info(json.__file__ )
    plpy.info("Server:" + server + " | port:" + port + " | login:" + str(login) + " | password:" + str(password))

    if login and password:
        neo4j.authenticate(server + ":" + port, login, password)

    for record in neo4j.Graph("http://" + server + ":" + port + "/db/data/").cypher.stream(query):
        keys = record.__producer__.columns

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
            else:
                jsonResult += json.dumps(object)

        jsonResult += "}"

        plpy.info("Result is :" + jsonResult)

        yield jsonResult


def cypher_with_server(plpy, query, server):
    """
        Make cypher query and return JSON result
    """

    sql = "SELECT unnest(srvoptions) AS conf FROM pg_foreign_server"
    if server:
        sql = "SELECT unnest(srvoptions) AS conf FROM pg_foreign_server WHERE srvname='" + server +"'"

    server = 'localhost'
    port = '7474'
    login = None
    password = None

    for row in plpy.cursor(sql):
        if row['conf'].startswith("server="):
            server = row['conf'].split("server=")[1]
        if row['conf'].startswith("port="):
            port = row['conf'].split("port=")[1]
        if row['conf'].startswith("user="):
            login = row['conf'].split("user=")[1]
        if row['conf'].startswith("password="):
            password = row['conf'].split("password=")[1]

    for result in cypher(plpy, query, server, port, login, password):
        yield result


def cypher_default_server(plpy, query):
    """
        Make cypher query and return JSON result
    """
    for result in cypher_with_server(plpy, query, None):
        yield result


def node2json(node):
    """
        Convert a py2neo node to json
    """
    jsonResult = "{"
    jsonResult += '"labels": ' + json.dumps(node.labels.resource.metadata) + ','
    jsonResult += '"properties": ' + json.dumps(node.properties)
    jsonResult += "}"

    return jsonResult


def relation2json(rel):
    """
        Convert a py2neo relation to json
    """

    jsonResult = "{"
    jsonResult += '"type": ' + json.dumps(rel.type) + ','
    jsonResult += '"properties": ' + json.dumps(rel.properties)
    jsonResult += "}"

    return jsonResult