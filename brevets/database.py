# THIS MODULE MUST BE USED IN A FLASK APP CONTEXT
import arrow
from flask import current_app, g
import pymongo
from pymongo import MongoClient

import util

MGFMT = "YYYY-MM-DDTHH:mm:ss"

def db_in_g():
    if 'dbclient' not in g:
        g.dbclient = MongoClient("mongodb://db:27017/")
    if 'db' not in g:
        g.db = g.dbclient["brevets"]
    if 'worksheets' not in g:
        g.worksheets = g.db.worksheets
    if current_app.testing == True:
        if 'worksheets_test' not in g:
            g.worksheets_test = g.db.worksheets_test

def init_db():
    db_in_g()
    data = util.random_worksheet_rows()
    ws = {
        "timestamp": arrow.utcnow().format(MGFMT),
        "worksheet": data,
        "start_time": "1982-01-01T00:00",
        "brevet_dist": 200
    }
    ws_count = g.worksheets.count_documents({})

    if current_app.testing == True:
        worksheets_test = g.db.worksheets_test
        g.worksheets_test = worksheets_test
        worksheets_test.drop()
        insert_worksheet(ws, g.worksheets_test)
    elif ws_count == 0 or ws_count is None:
        insert_worksheet(ws)


def insert_worksheet(worksheet, collection=None):
    ws = {
        "timestamp": arrow.utcnow().format(MGFMT),
        "start_time": worksheet["start_time"],
        "worksheet": worksheet["worksheet"],
        "brevet_dist": worksheet["brevet_dist"],
    }
    if collection is None:
        g.worksheets.insert_one(ws)
    else:
        collection.insert_one(ws)

def latest_worksheet(collection=None):
    if collection is None:
        collection = g.worksheets
    else:
        collection = collection
    document = collection.find_one(sort=[("timestamp", pymongo.DESCENDING)])
    worksheet = dict()
    if document is not None:
        worksheet["worksheet"] = document["worksheet"]
        worksheet["start_time"] = document["start_time"]
        worksheet["brevet_dist"] = document["brevet_dist"]
    elif collection.count_documents() == 0:
        worksheet["error"] = "No worksheets in the database yet!"
    else:
        worksheet["error"] = "This shouldn't happen"

    return worksheet

