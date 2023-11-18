import arrow
import flask

from flask_brevets import init_app
from database import init_db, insert_worksheet, latest_worksheet
from util import random_worksheet_rows

# Initialize a testing app
def init_test_app():
    app = init_app()
    app.config.update({"TESTING": True})
    return app

# Test whether or not insert_worksheet works. init_db calls this
def test_db_insert_a_worksheet():
    app = init_test_app()
    data = random_worksheet_rows()
    ws = {
        "worksheet": data,
        "start_time": "1982-01-01T00:00",
        "brevet_dist": 200
    }
    with app.test_request_context():
        init_db() # This adds a worksheet, testing an insertion for a total of 2

        insert_worksheet(ws, flask.g.worksheets_test)
        count = flask.g.worksheets_test.count_documents({})
        # since init_db added a worksheet and this test adds one, the count must be 2
        assert(count == 2)

def test_db_retrieve_a_worksheet():
    app = init_test_app()
    retreived = None
    with app.test_request_context():
        init_db()
        retreived = latest_worksheet(flask.g.worksheets_test)

    assert(retreived is not None)
