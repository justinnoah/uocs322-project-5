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
from acp_times import open_time, close_time, race_type

def test_0km_distance_open():
    start = arrow.get("2023-11-07 03:00")
    result = open_time(0, 200, start).format("YYYY-MM-DD HH:mm")
    print("start: %s" % start)
    print("result: %s" % result)
    actual = arrow.get(start.format("YYYY-MM-DD HH:mm")).format("YYYY-MM-DD HH:mm")
    print("actual: %s" % actual)
    assert actual == result

def test_0km_distance_close():
    start = arrow.get("2023-11-07 03:00")
    result = close_time(0, 200, start)
    print("start: %s" % start)
    print("result: %s" % result)
    actual = start.shift(hours=+1)
    print("actual: %s" % actual)
    assert actual == result

def test_open_220km_in_200km_brevet():
    start = arrow.get("2023-11-07 03:00")
    result = open_time(220, 200, start).format("YY-MM-DD HH:mm")
    print("start: %s" % start)
    print("result: %s" % result)
    actual = arrow.get(start.format("YYYY-MM-DD HH:mm")).shift(hours=+5, minutes=+53).format("YY-MM-DD HH:mm")
    print("actual: %s" % actual)
    assert actual == result

def test_close_220km_in_200km_brevet():
    race = race_type[200]
    start = arrow.get("2023-11-07 03:00")
    result = close_time(220, 200, start).format("YY-MM-DD HH:mm")
    print("start: %s" % start)
    print("result: %s" % result)
    actual = arrow.get(start.format("YYYY-MM-DD HH:mm")).shift(hours=+race["max_time"]).format("YY-MM-DD HH:mm")
    print("actual: %s" % actual)
    assert actual == result

def test_open_222km_in_600km_brevet():
    start = arrow.get("2023-11-07 03:00")
    result = open_time(222., 600., start)
    print("start: %s" % start)
    print("result: %s" % result)
    actual = arrow.get(start.format("YYYY-MM-DD HH:mm")).shift(hours=+6.566666666666)
    print("actual: %s" % actual)
    assert actual == result

def test_open_434km_in_600km_brevet():
    start = arrow.get("2023-11-07 03:00")
    result = open_time(434, 600, start).format("YY-MM-DD HH:mm")
    print("start: %s" % start)
    print("result: %s" % result)
    actual = arrow.get(start.format("YYYY-MM-DD HH:mm")).shift(hours=+13.266666).format("YY-MM-DD HH:mm")
    print("actual: %s" % actual)
    assert actual == result

def test_close_434km_in_600km_brevet():
    start = arrow.get("2023-11-07 03:00")
    result = close_time(434, 600, start).format("YY-MM-DD HH:mm")
    print("start: %s" % start)
    print("result: %s" % result)
    actual = arrow.get(start.format("YYYY-MM-DD HH:mm")).shift(hours=+28, minutes=+56).format("YY-MM-DD HH:mm")
    print("actual: %s" % actual)
    assert actual == result

