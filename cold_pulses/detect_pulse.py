# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 20:49:26 2020

@author: Robin
"""

import numpy as np

from cold_pulses.scripts_pulse.temp_stratification_index import \
                    temperature_stratification_index
from cold_pulses.scripts_pulse import filters, shifts, init_limits
from cold_pulses.scripts_pulse.metrics import output


def bot_pulse_detect(darray):
    """
    Algorithm to detect bot pulses from an xarray DataArray object.
    Returns a pandas DataFrame and an xarray Dataset containing all pulses
    information
    """
    # Extract sampling time step
    time_step = darray.time.diff('time').values[0]\
                           .astype('timedelta64[s]').astype(int)
    # For each time step, if one or more data value is a nan, the whole water
    # column temperature is set to nan.
    darray = darray.where(np.isnan(darray).sum('depth') == 0, np.nan)
    # Extract the deepest depth
    depth = darray.depth.max()
    # Compute TSI and rTSI
    tsi, r_tsi = temperature_stratification_index(darray)
    # Extract first start and end indexes for possible pulses
    starts, ends = init_limits.bot(tsi, r_tsi, darray,
                                   depth=depth)
    # Remove possible pulses that are too short
    starts, ends = filters.duration(starts, ends)
    # Remove possible pulses that do not show an important enough drop
    starts, ends = filters.max_drop(darray, starts, ends,
                                    depth=depth, kind='bot',
                                    step_number=1, total_steps=5)
    # Shift start indexes to the left to get real start indexes
    starts = shifts.starts(starts, ends, darray, tsi,
                           depth=depth, kind='bot',
                           step_number=2, total_steps=5)
    # Shift end indexes to the left to get real end indexes
    ends = shifts.ends(starts, ends, darray,
                       depth=depth, kind='bot',
                       step_number=3, total_steps=5)
    # Remove pulses that do not fit the specific TSI criterion
    starts, ends = filters.specific_tsi(darray, starts, ends, time_step,
                                        depth=depth, kind='bot',
                                        step_number=4, total_steps=5)
    # Remove overlap by combining overlapping pulses
    starts, ends = filters.remove_overlap(starts, ends)
    # Compute metrics and create output files
    df_out, ds_out = output(darray, starts, ends, time_step,
                            depth=depth, kind='bot',
                            step_number=5, total_steps=5)
    return df_out, ds_out

def top_pulse_detect(darray):
    """
    Algorithm to detect top pulses from an xarray DataArray object.
    Returns a pandas DataFrame and an xarray Dataset containing all pulses
    information
    """
    # Extract sampling time step
    time_step = darray.time.diff('time').values[0]\
                           .astype('timedelta64[s]').astype(int)
    # For each time step, if one or more data value is a nan, the whole water
    # column temperature is set to nan.
    darray = darray.where(np.isnan(darray).sum('depth') == 0, np.nan)
    # Extract the shallowest depth
    depth = darray.depth.min()
    # Compute TSI and rTSI
    tsi, r_tsi = temperature_stratification_index(darray)
    # Extract first start and end indexes for possible pulses
    starts, ends = init_limits.top(tsi, r_tsi, darray,
                                   depth=depth)
    # Remove possible pulses that are too short
    starts, ends = filters.duration(starts, ends)
    # Remove possible pulses that do not show an important enough drop
    starts, ends = filters.max_drop(darray, starts, ends,
                                    depth=depth, kind='top',
                                    step_number=1, total_steps=5)
    # Shift start indexes to the left to get real start indexes
    starts = shifts.starts(starts, ends, darray, tsi,
                           depth=depth, kind='top',
                           step_number=2, total_steps=5)
    # Shift end indexes to the left to get real end indexes
    ends = shifts.ends(starts, ends, darray,
                       depth=depth, kind='top',
                       step_number=3, total_steps=5)
    # Remove pulses that do not fit the specific TSI criterion
    starts, ends = filters.specific_tsi(darray, starts, ends, time_step,
                                        depth=depth, kind='top',
                                        step_number=4, total_steps=5)
    # Compute metrics and create output files
    df_out, ds_out = output(darray, starts, ends, time_step,
                            depth=depth, kind='top',
                            step_number=5, total_steps=5)
    return df_out, ds_out
