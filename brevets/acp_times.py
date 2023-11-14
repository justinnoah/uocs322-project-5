"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import math

import arrow

brevet_controls = {
    0:    { 'max_speed': 34.0 },
    200:  { 'min_speed': 15.0,   'max_speed': 32.0, 'max_time': 13.5 },
    400:  { 'min_speed': 15.0,   'max_speed': 30.0, 'max_time': 27.0 },
    600:  { 'min_speed': 15.0,   'max_speed': 28.0, 'max_time': 40.0 },
    1000: { 'min_speed': 11.428, 'max_speed': 26.0, 'max_time': 51.0 },
}

#  You MUST provide the following two functions
#  with these signatures. You must keep
#  these signatures even if you don't use all the
#  same arguments.
#
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
    rounded_control_km = round(control_dist_km)
    clamp_km = rounded_control_km if brevet_dist_km > rounded_control_km else brevet_dist_km
    start_time = arrow.get(brevet_start_time)
    hours_to_shift = 0

    for k, v in sorted(brevet_controls.items(), reverse=False):
        dist_over = clamp_km - k
        if dist_over > 0:
            clamp_km -= dist_over
            hours_to_shift = dist_over / v["max_speed"] + (1 / 120) # + 30sec for rounding reasons

    hours, minutes_float = math.modf(hours_to_shift)
    minutes = round(minutes_float *  60)
    return start_time.shift(hours=hours, minutes=minutes)


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
    rounded_control_km = round(control_dist_km)
    clamp_km = rounded_control_km if brevet_dist_km > rounded_control_km else brevet_dist_km
    start_time = arrow.get(brevet_start_time)
    hours_to_shift = 0

    # timing rules by spec
    if clamp_km <= 60:
        hours_to_shift = 1
        hours_to_shift += clamp_km / 20
    elif clamp_km >= brevet_dist_km:
        hours_to_shift = brevet_controls[brevet_dist_km]["max_time"]
    else:
        for k, v in brevet_controls.items():
            if k == 0:
                continue
            hours_to_shift += (k if k < clamp_km else clamp_km) / v["min_speed"]

    # Create hours and minutes from hours as float
    hours, minutes_float = math.modf(hours_to_shift)
    minutes = round(minutes_float *  60)
    # Return brevet_start_time shifted by calculated time
    return start_time.shift(hours=hours, minutes=minutes)

