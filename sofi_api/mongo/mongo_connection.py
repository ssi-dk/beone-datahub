import math
from datetime import datetime

import pymongo

CONNECTION_URIS = {}
CONNECTIONS = {}


def close_all_connections():
    """
    Internal use, closes all connections on exit
    """
    global CONNECTIONS
    for connection in CONNECTIONS.values():
        connection.close()


def add_URI(mongoURI, connection_name = "default"):
    """
    Saves a new connection. If name is unspecified it will be "default"
    """
    global CONNECTION_URIS
    CONNECTION_URIS[connection_name] = mongoURI


def get_connection(connection_name = "default"):
    """
    Returns a MongoClient object. Mostly for internal use
    """
    global CONNECTIONS
    if connection_name not in CONNECTIONS:
        CONNECTIONS[connection_name] = pymongo.MongoClient(
            CONNECTION_URIS[connection_name])
    return CONNECTIONS[connection_name]


# Utils


def date_now():
    """
    Needed to keep the same date in python and mongo, as mongo rounds to millisecond
    """
    d = datetime.utcnow()
    return d.replace(microsecond = math.floor(d.microsecond / 1000) * 1000)
