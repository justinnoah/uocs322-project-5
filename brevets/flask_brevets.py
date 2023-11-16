"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import copy
import logging
from os import error

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
        "worksheet": data,
        "start_time": "1982-01-01T00:00",
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
        "start_time": worksheet["start_time"],
        "worksheet": worksheet["worksheet"]
    }
    db.worksheets.insert_one(ws)

def latest_ws():
    document = db.worksheets.find_one(sort=[("timestamp", pymongo.DESCENDING)])
    worksheet = {"worksheet": {}, "start_time": "2021-01-21T00:00"}
    if document:
        worksheet["worksheet"] = document["worksheet"]
        worksheet["start_time"] = document["start_time"]
    return worksheet

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

    open_time = acp_times.open_time(km, control_dist, start_time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, control_dist, start_time).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

def validate_worksheet(worksheet):
    error_msg = ""
    # Validate the worksheet data has the right shape and keys
    keys = worksheet.keys()
    start_time_k = "start_time" in keys
    brevet_dist_k = "brevet_dist" in keys
    worksheet_k = "worksheet" in keys
    if not start_time_k:
        error_msg = "Missing Start Time"
    elif not brevet_dist_k:
        error_msg = "Missing Brevet Control Distance"
    elif not worksheet_k:
        error_msg = "Missing Worksheet Data"
    if error_msg != "":
        return error_msg

    # Validate brevet control distance
    try:
        # Make sure (regex) \d{3}\d?km is a proper brevet control distance
        bcd = round(float(worksheet["brevet_dist"]))
        # Range is (inclusive, exclusive)
        if bcd not in [200, 300, 400, 600, 1000]:
            error_msg = f"Invalid brevet control distance: '{bcd}'"
    except:
        error_msg = "Brevet Control Distance is invalid: \'{worksheet['brevet_dist']}\'"

    if error_msg != "":
        return error_msg

    # Validate no skipped rows
    # Start at the last row and work backwards.
    # There must be no empty rows before the final row entry
    latest_zero_row = len(worksheet["worksheet"])
    latest_valid_row = len(worksheet["worksheet"])
    for row in reversed(sorted(worksheet["worksheet"], key=lambda r: r["row"])):
        # If a zero row was found after a valid row, that's an error
        if latest_valid_row > latest_zero_row:
            error_msg = f"Invalid control distance in row \'{row['id']}\': \'{row['km']}\'"
            break

        curr_row_km = row["km"]
        if curr_row_km in ["0", 0, ""]:
            latest_zero_row = row['id']
        else:
            try:
                km = round(float(curr_row_km))
                latest_valid_row = row["id"]
            except:
                error_msg = f"Invalid control distance in row \'{row['id']}\': \'{row['km']}\'"
                return error_msg

    return error_msg


@app.route('/_save_worksheet', methods=["POST"])
def store_worksheet():
    worksheet = app.json.loads(request.get_data())
    app.logger.debug(f"Request Data: {worksheet}")

    message = validate_worksheet(worksheet)
    if message != "":
        insert_ws(worksheet)

    return flask.jsonify(message=message)

@app.route('/_restore_worksheet', methods=["GET"])
def send_worksheet():
    latest = latest_ws()
    app.logger.debug("SENDING WORKSHEET: %s" % latest)
    if latest:
        return flask.jsonify(data=latest)
    else:
        return flask.jsonify(data={})


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
