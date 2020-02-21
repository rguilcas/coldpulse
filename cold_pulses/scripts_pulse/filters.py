# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 10:53:05 2020

@author: Robin Guillaume-Castel

This file contains all filters used in pulse detection.
"""
import pandas as pd
import numpy as np
import xarray as xr
from cold_pulses.scripts_pulse.temp_stratification_index import \
                    temperature_stratification_index
from cold_pulses.scripts_pulse.prints import progress

def duration(starts, ends,
             min_duration=3):
    """
    starts and ends are np arrays representing the indexes of possible pulses
    min_duration is the minimum number of measurements that will be allowed
    between starts and ends

    Return 2 arrays starts and ends filtered by minimum duration
    """
    # Create a dataframe object with start and end indexes
    idx_dataframe = pd.DataFrame({'start':starts,
                                  'end':ends})
    # Compute duration
    idx_dataframe['duration'] = idx_dataframe.end - idx_dataframe.start
    # Filter pulses if the duration is below the min_duration
    idx_filtered = idx_dataframe.loc[idx_dataframe.duration >= min_duration]
    return idx_filtered.start.values, idx_filtered.end.values

def max_drop(darray, starts, ends,
             depth=25, cut_off=.01, kind='bot',
             step_number=1,
             total_steps=7):
    """
    darray is an xarray dataaarray of the temperature
    starts and ends are np arrays representing the indexes of possible pulses
    cut_off is the minimum drop allowed at the depth chosen

    Returns starts and ends indexes filtered taking only those associated with
    a drop in the depth desired.
    """
    # Create a dataframe object with start and end indexes
    idx_dataframe = pd.DataFrame({'start':starts,
                                  'end':ends})
    # Compute maximum drop for potential pulses
    all_drops = []
    for k in range(starts.size):
    # Extract start and end indexes
        start = starts[k]
        end = ends[k]
    # Print progress
        progress(start,
                 darray[0].size,
                 'Filtering drops',
                 step_number,
                 total_steps,
                 kind=kind)
    # Compute maximum drop
        drops = (darray[:, start] - darray[:, start:end]).max('time').values
    # Update maxmum drop list
        all_drops.append(drops)
    # Extract depth index
    index_depth = np.where(darray.depth == depth)[0][0]
    # Add maximum drop at the relevant depth to the dataframe earlier created
    all_drops = np.array(all_drops)
    idx_dataframe['drops'] = all_drops[:, index_depth]
    # Filter possible pulses if the maximum drop at the relevant depth is
    # smaller than cut_off
    df_filtered = idx_dataframe.loc[idx_dataframe.drops > cut_off]
    progress(1,
             1,
             'Filtering drops',
             step_number,
             total_steps,
             kind=kind)
    return df_filtered.start.values, df_filtered.end.values


def specific_tsi(darray, starts, ends, time_step,
                 depth=25, min_stsi=.04, kind='bot',
                 step_number=2,
                 total_steps=7):
    """
    darray is an xarray dataaarray of the temperature
    starts and ends are np arrays representing the indexes of possible pulses

    Compute stratification index by keeping only the effects of one specific depth
    """
    #Creating copy of the darray file to create sTSI time series
    darray_copy = xr.DataArray(np.copy(darray),
                               dims=['depth', 'time'],
                               coords={'depth':darray.depth,
                                       'time':darray.time})
    darray_copy[:] = np.nan
    length = darray.shape[1]
    # Extract relevant depth
    index_depth = int(np.where(darray.depth == depth)[0][0])
    # Extract all irrelevant depths
    slicing = np.array([True]*darray.depth.size)
    slicing[index_depth] = False
    # For each pulse, create a fake temperature time series for irrelevant
    # depths to compute sTSI
    for k in range(starts.size):
    # Extract start and end indexes
        start = starts[k]
        end = ends[k]
    # Print progress
        progress(start,
                 darray[0].size,
                 'Filtering specific TSI',
                 step_number,
                 total_steps,
                 kind=kind)
    # Exctract initial values
        init_value = darray[index_depth, start].values
    # Prepare a linear interpolation between start and end values
        interpolation = np.nan*np.zeros((darray_copy.depth.size-1,
                                         end - start + 2))
        interpolation[:, 0] = darray[index_depth, max(0, start - 1)]
        interpolation[:, -1] = darray[index_depth, min(end, length - 1)]
    # Create a dataframe that will be used for interpolation
        interpolation_dataframe = pd.DataFrame(interpolation.transpose())
    # Interpolate
        interpolation = interpolation_dataframe.interpolate().values.\
                        transpose()[:, 1:-1]
    # Create an xarray DataArray of the interpolation
        interpolation = xr.DataArray(interpolation,
                                     dims=['depth', 'time'],
                                     coords={'depth':darray.depth[slicing],
                                             'time':darray_copy\
                                                 [slicing, start:end].time})
    # If the interpolation is greater than the init value: init value
        interpolation = interpolation.\
                        where(interpolation < init_value, init_value)
    # If the interpolation is greater than the origninal temperature series:
    # original temperature
        interpolation = interpolation.\
                        where(interpolation < darray[slicing, start:end],
                              darray[slicing, start:end])
    # If the interpolation is smaller than the relevant depth's temperature:
    # relevant depth's temperature
        interpolation = interpolation.\
                        where(interpolation > darray[index_depth, start:end],
                              darray[index_depth, start:end])
    # Add the newly computed temperature time series to the darray_copy series
        darray_copy[slicing, start:end] = interpolation
        darray_copy[index_depth, start:end] = darray[index_depth, start:end]
    progress(1,
             1,
             'Filtering specific TSI',
             step_number,
             total_steps,
             kind=kind)
    # Compute specific TSI
    s_tsi = temperature_stratification_index(darray_copy, daily=False)
    # Compute extremum of specific TSI for each possible pulse
    # Maximum sTSI for top pulses, minimum for bottom pulses
    ext_stsi_list = []
    for k in range(starts.size):
    # Extract start and end indexes
        start = starts[k]
        end = ends[k]
    # Compute maximum or minimum sTSI depending on the pulse type studied
        if kind == 'top':
            min_strat = s_tsi[start:end].max()
        elif kind == 'bot':
            min_strat = s_tsi[start:end].min()
    # Update the extreme sTSI list
        ext_stsi_list.append(min_strat.values)
    # Create dataframe with start, end and extreme sTSI
    stsi_dataframe = pd.DataFrame({'start':starts,
                                   'end':ends,
                                   'min_strat':ext_stsi_list})
    # Filter pulses if sTSI magnitude is smaller than min_stsi
    if kind == 'bot':
        df_filtered = stsi_dataframe.loc[stsi_dataframe.min_strat < -min_stsi]
    elif kind == 'top':
        df_filtered = stsi_dataframe.loc[stsi_dataframe.min_strat > min_stsi]
    return df_filtered.start.values, df_filtered.end.values

def remove_overlap(starts, ends):
    """
    starts and ends are np arrays representing the indexes of possible pulses

    Removes overlapping values of start and end to combine pulses
    Returns new arrays of starts and ends indexes
    """
    #Create a time series showing pulse presence:
    # 1 if there is a pulse, 0 if not
    pulse_presence = np.zeros(ends[-1])
    for k in range(starts.size):
        start = starts[k]
        end = ends[k]
        pulse_presence[start:end] = 1
    # Compute new start and end indexes being the start and end indexes
    # surrounding a continuous period of pulse presence
    new_starts = np.where(np.diff(pulse_presence) > 0)[0]
    new_ends = np.where(np.diff(pulse_presence) < 0)[0]
    # Add potential extreme values to the new starts and ends
    if pulse_presence[0] == 1:
        new_starts = np.insert(new_starts, 0, 0)
    if pulse_presence[-1] == 1:
        new_ends = np.insert(new_ends, new_ends.size, ends[-1])
    return new_starts, new_ends
