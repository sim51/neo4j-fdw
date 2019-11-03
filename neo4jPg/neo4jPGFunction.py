from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
from neo4j import GraphDatabase, basic_auth, CypherError, __version__ as neo4jversion
import json
import ast

MAJOR,MINOR,PATCH = neo4jversion.split('.')

"""
Neo4j Postgres function
"""
def cypher(plpy, query, params, url, login, password):
    """
        Make cypher query and return JSON result
    """
    driver = GraphDatabase.driver( url, auth=basic_auth(login, password))
    session = driver.session()
    log_to_postgres("Cypher function with query " + query + " and params " + unicode(params), DEBUG)

    # Execute & retrieve neo4j data
    try:
        for record in session.run(query, ast.literal_eval(params)):
            jsonResult  = "{"
            for key in record.keys():
                if len(jsonResult) > 1:
                    jsonResult += ","
                jsonResult += '"' + key + '":'
                object = record[key]
                if object.__class__.__name__ == "Node":
                    jsonResult += node2json(object)

                # In 1.6 series of neo4j python driver a change to way relationship types are
                # constructed which means ABCMeta is __class__ and the mro needs to be checked
                elif (MAJOR >= 1 and MINOR > 16) and any(c.__name__ == 'Relationship' for c in object.__class__.__mro__):
                    jsonResult += relation2json(object)
                elif object.__class__.__name__ == "Relationship":
                    jsonResult += relation2json(object)

                elif object.__class__.__name__ == "Path":
                    jsonResult += path2json(object)
                else:
                    jsonResult += json.dumps(object)
            jsonResult += "}"
            yield jsonResult
    except CypherError:
        raise RuntimeError("Bad cypher query : " + statement)
    finally:
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
    jsonResult += '"id": ' + json.dumps(node._id) + ','
    jsonResult += '"labels": ' + json.dumps(node._labels, default=set_default) + ','
    jsonResult += '"properties": ' + json.dumps(node._properties, default=set_default)
    jsonResult += "}"

    return jsonResult


def relation2json(rel):
    """
        Convert a relation to json
    """
    jsonResult = "{"
    jsonResult += '"id": ' + json.dumps(rel._id) + ','

    if (MAJOR >= 1 and MINOR > 16):
        # In 1.6 series of neo4j python driver relationships have "type" attribute instead of "_type"
        jsonResult += '"type": ' + json.dumps(rel.type) + ','
        # In 1.6 series of neo4j python driver relationships contain their nodes
        jsonResult += '"nodes": [' + node2json(rel.nodes[0]) + ',' + node2json(rel.nodes[1]) + '],'
    else:
        jsonResult += '"type": ' + json.dumps(rel._type) + ','

    jsonResult += '"properties": ' + json.dumps(rel._properties, default=set_default)
    jsonResult += "}"

    return jsonResult

def path2json(path):
    """
        Convert a path to json
    """
    jsonResult = "["

    if (MAJOR >= 1 and MINOR > 16):
        jsonResult += ",".join([relation2json(segment) for segment in path])
    else:
        # This seems to be broken?
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
