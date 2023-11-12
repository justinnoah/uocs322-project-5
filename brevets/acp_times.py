"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import math
from enum import Enum

import arrow
from flask import current_app as app

race_type = {
    200.0:  { 'dist': 200.0, 'min_speed': 15.0,   'max_speed': 34.0, 'max_time': 13.5 },
    300.0:  { 'dist': 100.0, 'min_speed': 15.0,   'max_speed': 32.0, 'max_time': 20.0 },
    400.0:  { 'dist': 200.0, 'min_speed': 15.0,   'max_speed': 32.0, 'max_time': 27.0 },
    600.0:  { 'dist': 200.0, 'min_speed': 15.0,   'max_speed': 30.0, 'max_time': 40.0 },
    1000.0: { 'dist': 400.0, 'min_speed': 11.428, 'max_speed': 28.0, 'max_time': 51.0 },
}

#  You MUST provide the following two functions
#  with these signatures. You must keep
#  these signatures even if you don't use all the
#  same arguments.
#
class OC(Enum):
    OPEN = 1
    CLOSE = 2

def shift_time(
        control_dist_km: float,
        brevet_dist_km: float,
        brevet_start_time: arrow.arrow.Arrow,
        oc: OC
) -> arrow.arrow.Arrow:
    brevet_start_time = arrow.get(brevet_start_time.format("YYYY-MM-DD HH:mm"))
    # Clamp the lower bound for control and brevet distances at 0km
    if control_dist_km < 0.:
        control_dist_km = 0.
    if brevet_dist_km < 0.:
        brevet_dist_km = 0.

    # Prep for open / close differences
    minmax = None
    if oc == OC.OPEN:
        minmax = 'max'
        if control_dist_km == 0.0:
            return brevet_start_time
    elif oc == OC.CLOSE:
        minmax = 'min'
        if control_dist_km == 0.0:
            return brevet_start_time.shift(hours=+1)
    speed = "%s_speed" % minmax
    print("speed: %s" % speed)

    # Clamp distance to 120%
    print("distance: %s" % control_dist_km)
    if control_dist_km > brevet_dist_km:
        control_dist_km = brevet_dist_km
    print("post clamp distance: %s" % control_dist_km)

    current_brevet_range = race_type[brevet_dist_km]
    print("Using brevet: %s - %s" % (brevet_dist_km, current_brevet_range))

    # Make a sorted list of the distances we will be calculating with
    distances = list(race_type.keys())
    distances.sort()
    print("distances to use in calcs: %s" % distances)

    if brevet_dist_km == 200.:
        distances = [distances[0]]

    # Remove the ones we aren't using
    while len(distances) >= 2:
        if not (control_dist_km > distances[-2] and control_dist_km < distances[-1]):
            # Throw the value away
            distances.pop()
        else:
            break
    print("Clamped distances: %s" % distances)

    # Amount to shift start time by in hours
    shift = 0.0
    closed = False

    while len(distances) > 0:
        # The control segment to calculate from
        control_dist = distances[-1]
        segment = race_type[control_dist]

        # Add to shift for each segment
        if control_dist_km >= control_dist:
            if oc == OC.OPEN:
                if not closed:
                    shift += math.ceil(segment['dist'] / segment[speed] * 60) / 60.
            else:
                if not closed:
                    shift += segment['max_time']
                    closed = True
        else:
            if control_dist >= 300.:
                seg_dist = math.ceil(control_dist_km - distances[-2])
                seg_time = math.ceil(seg_dist / race_type[distances[-2]][speed] * 60.) / 60.
                shift += seg_time
            else:
                seg_dist = math.ceil(control_dist_km)
                seg_time = math.ceil(seg_dist / race_type[200.][speed])
                shift += seg_time
        distances.pop()
        print("shifting... %s" % shift)

    print("shifting: %s hours..." % shift)
    return brevet_start_time.shift(hours=+shift)


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, control distance in kilometers
       brevet_dist_km: number, nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An arrow object
    Returns:
       An arrow object indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    return shift_time(control_dist_km, brevet_dist_km, brevet_start_time, OC.OPEN)

def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, control distance in kilometers
       brevet_dist_km: number, nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An arrow object
    Returns:
       An arrow object indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    return shift_time(control_dist_km, brevet_dist_km, brevet_start_time, OC.CLOSE)

