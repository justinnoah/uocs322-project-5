"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import logging
from typing import final

import arrow
import flask
from flask import request

import acp_times  # Brevet time calculations
import database as db
import config

###
# Globals
###
def init_app():
    app = flask.Flask(__name__)
    with app.app_context():
        app.before_request(db.db_in_g)
        db.init_db()
    return app


app = init_app()
CONFIG = config.configuration()
DTFMT = 'YYYY-MM-DDTHH:mm'

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
        return "Missing Start Time"
    elif not brevet_dist_k:
        return "Missing Brevet Control Distance"
    elif not worksheet_k:
        return "Missing Worksheet Data"

    # Validate brevet control distance
    try:
        # Make sure (regex) \d{3}\d?km is a proper brevet control distance
        bcd = round(float(worksheet["brevet_dist"]))
        # Range is (inclusive, exclusive)
        if bcd not in [200, 300, 400, 600, 1000]:
            return f"Invalid brevet control distance: '{bcd}km'"
    except:
        return "Brevet Control Distance is invalid: '{worksheet['brevet_dist']}'"

    # Validate no skipped rows
    # Start at the last row and work backwards.
    # There must be no empty rows before the final row entry
    final_row_id = -1
    the_worksheet = worksheet["worksheet"]
    brevet_dist = round(float(worksheet["brevet_dist"]))
    # allow for a maximum final control km of 20% over the brevet control
    prev_km = brevet_dist * 1.2 
    # Reversed row order to skip over the empty lines of the worksheet more easily
    for row in reversed(sorted(the_worksheet, key=lambda r: r["row_id"])):
        _id = int(row['row_id'])
        id_one_idxd = _id + 1
        km = row['km']
        zeros = ["0", 0]

        # Skip empty rows at the bottom of the worksheet
        if _id != 0 and (km == "" or km is None) and final_row_id == -1:
            continue

        if _id == 0 and not (km in ["0", 0]):
            return f"The first line in the worksheet must be 0."


        # Check for an empty line within the control rows of the worksheet
        if (km in zeros or km is None) and final_row_id != -1 and _id != 0:
            return f"Invalid kilometers in row {id_one_idxd}"

        try:
            brevet_dist = round(float(brevet_dist))
        except:
            return f"An invalid brevet control distance received: '{brevet_dist}'"

        # Parse the kilometers of this row as an int, return an error otherwise
        try:
            row['km'] = round(float(row['km']))
            km = row['km']
        except:
            return f"Unable to parse '{row['km']}' as a number."

        # The first row with something in the km slot has been found
        if km > 0 and final_row_id == -1:
            if km > prev_km:
                return f"The final control distance must be between {brevet_dist} and {prev_km}."
            # If the last row in the worksheet has a value less than brevet_dist, that's an error
            if km < brevet_dist:
                return f"The final control point ({km}km) must be at least ({brevet_dist}km). Please try again."
            final_row_id = _id

        # Verify the kilometers in the rows grow sequentially
        if km > prev_km and final_row_id != -1:
            return f"{km}km in row {id_one_idxd} is greater than {prev_km}km in row {id_one_idxd + 1}."

        if km > 0 and final_row_id != -1:
            prev_km = km

        # If this is the first row of the worksheet and it is empty in the km slot, error
        if _id == 0 and final_row_id == -1:
            return f"The worksheet is empty, not submitting."

    return f""

@app.route('/_save_worksheet', methods=["POST"])
def store_worksheet():
    worksheet = app.json.loads(request.get_data())
    app.logger.debug(f"Request Data: {worksheet}")

    message = validate_worksheet(worksheet)
    if message == "":
        db.insert_worksheet(worksheet)

    return flask.jsonify(message=message)

@app.route('/_restore_worksheet', methods=["GET"])
def send_worksheet():
    latest = db.latest_worksheet()
    app.logger.debug("SENDING WORKSHEET: %s" % latest)
    return flask.jsonify(data=latest)

#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
