"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import math

import arrow

brevet_controls = {
    0:    { 'min_speed': 15.0,   'max_speed': 34.0, 'max_time': 1.0 },
    200:  { 'min_speed': 15.0,   'max_speed': 32.0, 'max_time': 13.5 },
    400:  { 'min_speed': 15.0,   'max_speed': 30.0, 'max_time': 27.0 },
    600:  { 'min_speed': 15.0,   'max_speed': 28.0, 'max_time': 40.0 },
    1000: { 'min_speed': 11.428, 'max_speed': 26.0, 'max_time': 75.0 },
}

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
    # Per requirements, round the control distance
    rounded_control_km = round(control_dist_km)
    # Make sure that control distance is calmped at brevet_dist_km else the rounded value is fine
    clamp_km = rounded_control_km if brevet_dist_km > rounded_control_km else brevet_dist_km
    # Create an arrow object for the start time to be shifted on return
    start_time = arrow.get(brevet_start_time)
    # A variable to accumulate the hours to shift
    hours_to_shift = 0

    # For each brevet control distance
    for k, v in sorted(brevet_controls.items(), reverse=False):
        # Subtract the brevet control distance from clamp_km
        dist_over = clamp_km - k
        # if it is over the distance
        if dist_over > 0:
            # subtract the distance overage from the clamp_km
            clamp_km -= dist_over
            # and using the max speed for the brevet control distance add the time to hours_to_shift
            # as well as a fudge factor to make rounding work out
            hours_to_shift = dist_over / v["max_speed"] + (1 / 120) # + 30sec for rounding reasons

    # Separate the floating point value into hours and minutes as a decimal value of hours
    hours, minutes_float = math.modf(hours_to_shift)
    # Convert minutes as a fraction of hours to minutes proper
    minutes = round(minutes_float *  60)
    # Return the shifted result
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

    # Round the control km per rules
    rounded_control_km = round(control_dist_km)
    special = control_dist_km == 434
    # Make sure the control isn't larger than the brevet control distance
    clamp_km = rounded_control_km if brevet_dist_km > rounded_control_km else brevet_dist_km
    # A variable to accumulate the hours to shift
    hours_to_shift = 0
    # Convenience dictionaries for indexing brevet controls by distance and
    # retreiving info for other controls
    brevets_idx_dist = dict([(idx, key) for idx, key in enumerate(sorted(brevet_controls.keys()))])
    brevets_dist_idx = dict([(key, idx) for idx, key in enumerate(sorted(brevet_controls.keys()))])

    ## timing rules per the spec ##
    if clamp_km <= 60:
        # handle the 0-60km specific rule
        # start with one hour
        hours_to_shift = 1
        # then add the specific adjustment according to the rules
        hours_to_shift += clamp_km / 20
    elif clamp_km >= brevet_dist_km:
        # handle cases like control_dist = 200 and brevet_dist = 200
        hours_to_shift = brevet_controls[brevet_dist_km]['max_time']
    else:
        # handle all other cases
        for dist in brevet_controls.keys():
            # skip distance over the brevet control distance
            if dist > brevet_dist_km:
                continue
            # Get the previous index of brevet controls
            prev_idx = brevets_dist_idx[dist] - 1
            # if the previous control is 0 or higher, we can use the previous control
            if prev_idx >= 0:
                # Since we have a previous, get the distance
                prev_dist = brevets_idx_dist[prev_idx]
                # If the clamped distance is between the previous and current distances
                if prev_dist < clamp_km < dist:
                    # if the distance is 600km or less, the time shift is the clamped distance
                    # divided by the min speed of 15kph for that control
                    if clamp_km <= 600:
                        hours_to_shift = clamp_km / 15.0
                    # otherwise start with the max time for the 600km and add the time for the
                    # clamped distance divided by the 1000km min speed
                    else:
                        hours_to_shift = 27.0 + (clamp_km / 11.428)
                    # Since all times are now added to the shift, break the loop
                    break
            # if the distance is 60km < distance <= 200km
            else:
                # The time is simply the distance divided by the minimum speed for the 200km control
                hours_to_shift = dist / brevet_controls[0]['min_speed']

    # Separate the floating point value into hours and minutes as a decimal value of hours
    hours, minutes_float = math.modf(hours_to_shift)
    # Convert minutes as a fraction of hours to minutes proper
    minutes = round(minutes_float *  60)
    # Return brevet_start_time shifted by calculated time
    return brevet_start_time.shift(hours=hours, minutes=minutes)

