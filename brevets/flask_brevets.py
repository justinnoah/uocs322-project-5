"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import copy
import logging

import arrow
import flask
from flask import request

import acp_times  # Brevet time calculations
import config
from pymongo import MongoClient
import pymongo

def init_db():
    client = MongoClient("mongodb://db:27017/")
    db = client["brevets"]

    datum = {'km': 0, 'loc': "", 'row': 0}
    data = []
    for i in range(0, 20):
        d = copy.deepcopy(datum)
        d['row'] += i
        data.append(d)
    ws = {
        "timestamp": arrow.utcnow().format(MGFMT),
        "worksheet": data
    }
    db.worksheets.insert_one(ws)
    return (client, db)

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
DTFMT = 'YYYY-MM-DDTHH:mm'
MGFMT = f"{DTFMT}:ss"
(client, db) = init_db()


def insert_ws(worksheet):
    ws = {
        "timestamp": arrow.utcnow().format(MGFMT),
        "worksheet": worksheet
    }
    db.worksheets.insert_one(ws)

def latest_ws():
    document = db.worksheets.find_one(sort=[("timestamp", pymongo.DESCENDING)])
    if document:
        return document["worksheet"]
    else:
        return None

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999., type=float)
    start_time = arrow.get(request.args.get('start_time', arrow.now().format(DTFMT), type=str), DTFMT)
    control_dist = request.args.get("control_dist", 200, type=int)

    # FIXME!
    # Right now, only the current time is passed as the start time
    # and control distance is fixed to 200
    # You should get these from the webpage!
    open_time = acp_times.open_time(km, control_dist, start_time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, control_dist, start_time).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route('/_save_worksheet', methods=["POST"])
def store_worksheet():
    data = app.json.loads(request.get_data())
    app.logger.debug(f"Request Data: {data}")
    insert_ws(data)
    return "", 200

@app.route('/_restore_worksheet', methods=["GET"])
def send_worksheet():
    latest = latest_ws()
    app.logger.debug("data: %s" % latest)
    if latest:
        return flask.jsonify(worksheet=latest)
    else:
        return flask.jsonify(worksheet={})


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
