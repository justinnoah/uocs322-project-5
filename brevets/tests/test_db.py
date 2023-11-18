import arrow
import flask

from flask_brevets import init_app
from database import init_db, insert_worksheet, MGFMT
from util import random_worksheet_rows

def init_test_app():
    app = init_app()
    app.config.update({"TESTING": True})
    return app

def test_db_init_creates_one_worksheet():
    app = init_test_app()
    with app.test_request_context():
        init_db()
        count = flask.g.worksheets_test.count_documents({})
        assert(count == 1)

def test_db_add_a_2nd_worksheet():
    app = init_test_app()
    count = 0
    with app.test_request_context():
        init_db()
        random_rows = random_worksheet_rows()
        ws = {
            "timestamp": arrow.utcnow().format(MGFMT),
            "worksheet": random_rows,
            "start_time": "1982-01-01T00:00",
            "brevet_dist": 200
        }
        insert_worksheet(ws, flask.g.worksheets_test)
        count = flask.g.worksheets_test.count_documents({})

    assert(count == 2)
