"""
Nose tests for acp_times.py

Write your tests HERE AND ONLY HERE.
"""

import nose    # Testing framework
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

import arrow
from acp_times import open_time, close_time, brevet_controls as race_type
from flask_brevets import DTFMT

def test_0km_distance_open():
    start = arrow.get("2023-11-07T03:00")
    result = open_time(0, 200, start).format(DTFMT)
    print("start: %s" % start.format(DTFMT))
    print("result: %s" % result)
    actual = arrow.get(start.format(DTFMT)).format(DTFMT)
    print("actual: %s" % actual)
    assert actual == result

def test_0km_distance_close():
    start = arrow.get("2023-11-07T03:00")
    result = close_time(0, 200, start)
    print("start: %s" % start.format(DTFMT))
    print("result: %s" % result)
    actual = start.shift(hours=+1).format(DTFMT)
    start = start.format(DTFMT)
    print("actual: %s" % actual)
    assert actual == result.format(DTFMT)

def test_open_220km_in_200km_brevet():
    start = arrow.get("2023-11-07T03:00")
    result = open_time(220, 200, start).format(DTFMT)
    print("start: %s" % start.format(DTFMT))
    print("result: %s" % result)
    actual = arrow.get(start).shift(hours=+5, minutes=+53).format(DTFMT)
    print("actual: %s" % actual)
    assert actual == result

def test_close_220km_in_200km_brevet():
    race = race_type[200]
    start = arrow.get("2023-11-07T03:00")
    result = close_time(220, 200, start).format(DTFMT)
    print("start: %s" % start.format(DTFMT))
    print("result: %s" % result)
    actual = arrow.get(start).shift(hours=+race["max_time"]).format(DTFMT)
    print("actual: %s" % actual)
    assert actual == result

def test_open_222km_in_600km_brevet():
    start = arrow.get("2023-11-07T03:00")
    result = open_time(222, 600, start).format(DTFMT)
    print("start: %s" % start.format(DTFMT))
    print("result: %s" % result)
    actual = arrow.get(start).shift(hours=+6.54).format(DTFMT)
    print("actual: %s" % actual)
    assert actual == result

def test_open_434km_in_600km_brevet():
    start = arrow.get("2023-11-07T03:00")
    result = open_time(434, 600, start).format(DTFMT)
    print("start: %s" % start.format(DTFMT))
    print("result: %s" % result)
    actual = arrow.get(start).shift(hours=+12.77).format(DTFMT)
    print("actual: %s" % actual)
    assert actual == result

def test_close_434_in_600km_brevet():
    start = arrow.get("2023-11-07T03:00")
    result = close_time(434, 600, start).format(DTFMT)
    print(f"start: {start.format(DTFMT)}")
    print(f"result: {result}")
    actual = arrow.get(start).shift(hours=28, minutes=56).format(DTFMT)
    print(f"actual: {actual}")
    assert actual == result
