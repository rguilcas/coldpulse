# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 20:49:26 2020

@author: Robin
"""

import numpy as np

from cold_pulses.scripts_pulse.temp_stratification_index import \
                    temperature_stratification_index
from cold_pulses.scripts_pulse.init_start_end import init_top, init_bot
from cold_pulses.scripts_pulse.filters import (filter_by_duration,
                                               filter_by_drop,
                                               filter_true_stratification,
                                               remove_overlap)
from cold_pulses.scripts_pulse.shifts import shift_ends, shift_starts
from cold_pulses.scripts_pulse.metrics import output


def bot_pulse_detect(darray):
    """
    Algorithm to detect bot pulses from an xarray DataArray object.
    Returns a pandas DataFrame and an xarray Dataset containing all pulses
    information
    """
    # Extranct sampling time step
    time_step = darray.time.diff('time').values[0]\
                           .astype('timedelta64[s]').astype(int)
    # For each time step, if one or more data value is a nan, the whole water
    # column temperature is set to nan.
    darray = darray.where(np.isnan(darray).sum('depth') == 0, np.nan)
    # Extract the deepest depth
    depth = darray.depth.max()
    # Compute TSI and rTSI
    tsi, rtsi = temperature_stratification_index(darray, time_step)
    # Extract first start and end indexes for possible pulses
    starts, ends = init_bot(tsi, rtsi, darray,
                            depth=depth)
    # Remove possible pulses that are too short
    starts, ends = filter_by_duration(starts, ends)
    # Remove possible pulses that do not show an important enough drop
    starts, ends = filter_by_drop(darray, starts, ends,
                                  depth=depth, kind='bot',
                                  step_number=1, total_steps=5)
    # Shift start indexes to the left to get real start indexes
    starts = shift_starts(starts, ends, darray, tsi,
                          depth=depth, kind='bot',
                          step_number=2, total_steps=5)
    # Shift end indexes to the left to get real end indexes
    ends = shift_ends(starts, ends, darray,
                      depth=depth, kind='bot',
                      step_number=3, total_steps=5)
    # Remove pulses that do not fit the specific TSI criterion
    starts, ends = filter_true_stratification(darray, starts, ends, time_step,
                                              depth=depth, kind='bot',
                                              step_number=4, total_steps=5)
    # Remove overlap by combining overlapping pulses
    starts, ends = remove_overlap(starts, ends)
    # Create output files
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
    time_step = darray.time.diff('time').values[0]\
                           .astype('timedelta64[s]').astype(int)
    darray = darray.where(np.isnan(darray).sum('depth') == 0, np.nan)
    depth = darray.depth.min()
    tsi, daily_tsi = temperature_stratification_index(darray, time_step)
    starts, ends = init_top(tsi, daily_tsi)
    starts, ends = filter_by_duration(starts, ends)
    starts, ends = filter_by_drop(darray, starts, ends,
                                  depth=depth, kind='top',
                                  step_number=1, total_steps=5)
    starts = shift_starts(starts, ends, darray, tsi,
                          depth=depth, kind='top',
                          step_number=2, total_steps=5)
    ends = shift_ends(starts, ends, darray,
                      depth=depth, kind='top',
                      step_number=3, total_steps=5)
    starts, ends = filter_true_stratification(darray, starts, ends, time_step,
                                              depth=depth, kind='top',
                                              step_number=4, total_steps=5)
    df_out, ds_out = output(darray, starts, ends, time_step,
                            depth=depth, kind='top',
                            step_number=5, total_steps=5)
    return df_out, ds_out
