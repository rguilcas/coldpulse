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


def bot_pulse_detect(darray, config_data):
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
    tsi, r_tsi = temperature_stratification_index(darray,
                                                  num_days_rolling=config_data\
                                                  ['rtsi_num_days'])
    # Extract first start and end indexes for possible pulses
    starts, ends = init_limits.bot(tsi, r_tsi, darray,
                                   depth=depth)
    # Remove possible pulses that are too short
    if config_data['filter_min_duration']:
        starts, ends = filters.duration(starts, ends, time_step,
                                        min_duration=config_data['min_duration'])
    if config_data['filter_max_duration']:
        starts, ends = filters.duration(starts, ends, time_step,
                                        max_duration=config_data['max_duration'])
    # Remove possible pulses that do not show an important enough drop
    if config_data['filter_min_drop']:
        starts, ends = filters.max_drop(darray, starts, ends,
                                        depth=depth, kind='bot',
                                        step_number=1, total_steps=4,
                                        cut_off=config_data['min_drop'])
    else:
        starts, ends = filters.max_drop(darray, starts, ends,
                                        depth=depth, kind='bot',
                                        step_number=1, total_steps=4,
                                        cut_off=0)
    # Shift end indexes to the left to get real end indexes
    ends = shifts.ends(starts, ends, darray, time_step,
                       depth=depth, kind='bot',
                       step_number=2, total_steps=4,
                       num_right_max=config_data['num_right_max'])
    # Remove pulses that do not fit the specific TSI criterion
    if config_data['filter_stsi']:
        starts, ends = filters.specific_tsi(darray, starts, ends, time_step, r_tsi,
                                            depth=depth, kind='bot',
                                            step_number=3, total_steps=4,
                                            min_stsi=config_data['min_stsi'])
    # Remove overlap by combining overlapping pulses
    starts, ends = filters.remove_overlap(starts, ends)
    # Compute metrics and create output files
    df_out, ds_out = output(darray, starts, ends, time_step,
                            depth=depth, kind='bot',
                            step_number=4, total_steps=4)
    return df_out, ds_out

def top_pulse_detect(darray, config_data):
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
    tsi, r_tsi = temperature_stratification_index(darray,
                                                  num_days_rolling=config_data\
                                                  ['rtsi_num_days'])
    # Extract first start and end indexes for possible pulses
    starts, ends = init_limits.top(tsi, r_tsi, darray,
                                   depth=depth)
    # Remove possible pulses that are too short
    if config_data['filter_min_duration']:
        starts, ends = filters.duration(starts, ends, time_step,
                                        min_duration=config_data['min_duration'])
    if config_data['filter_max_duration']:
        starts, ends = filters.duration(starts, ends, time_step,
                                        max_duration=config_data['max_duration'])
    # Remove possible pulses that do not show an important enough drop
    if config_data['filter_min_drop']:
        starts, ends = filters.max_drop(darray, starts, ends,
                                        depth=depth, kind='top',
                                        step_number=1, total_steps=4,
                                        cut_off=config_data['min_drop'])
    else:
        starts, ends = filters.max_drop(darray, starts, ends,
                                        depth=depth, kind='top',
                                        step_number=1, total_steps=4,
                                        cut_off=0)
        
    # Shift end indexes to the left to get real end indexes
    ends = shifts.ends(starts, ends, darray, time_step,
                       depth=depth, kind='bot',
                       step_number=2, total_steps=4,
                       num_right_max=config_data['num_right_max'])
    # Remove pulses that do not fit the specific TSI criterion
    if config_data['filter_stsi']:
        starts, ends = filters.specific_tsi(darray, starts, ends, time_step, r_tsi,
                                            depth=depth, kind='top',
                                            step_number=3, total_steps=4,
                                            min_stsi=config_data['min_stsi'])
    # Remove overlap by combining overlapping pulses
    starts, ends = filters.remove_overlap(starts, ends)
    # Compute metrics and create output files
    df_out, ds_out = output(darray, starts, ends, time_step,
                            depth=depth, kind='bot',
                            step_number=4, total_steps=4)
    return df_out, ds_out

