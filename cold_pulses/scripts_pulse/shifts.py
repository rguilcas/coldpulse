# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:56:43 2020

@author: Robin
"""
import numpy as np
import pandas as pd
from cold_pulses.scripts_pulse.prints import progress

def starts(starts, ends, darray, tsi,
           depth=25,
           step_number=3,
           total_steps=7,
           kind='bot'):
    """
    Shift start indexes to the left to get proper pulse start
    """
    depth_index = np.where(darray.depth == depth)[0][0]
    # Where is nan field
    nan_list_idx = np.where(np.isnan(darray[depth_index]))[0]
    # Where relevant T is the maximum temp in depth
    max_temp_list_idx = np.where(darray[depth_index] == darray.max('depth'))[0]
    # Were the tsi is opposite to what it should be
    if kind == 'bot':
        tsi_out_list_idx = np.where(tsi > 0)[0]
    elif kind == 'top':
        tsi_out_list_idx = np.where(tsi < 0)[0]
    # Add zero to all arrays
    if 0 not in nan_list_idx:
        nan_list_idx = np.insert(nan_list_idx, 0, 0)
    if 0 not in max_temp_list_idx:
        max_temp_list_idx = np.insert(max_temp_list_idx, 0, 0)
    if 0 not in tsi_out_list_idx:
        tsi_out_list_idx = np.insert(tsi_out_list_idx, 0, 0)
    # Create array for new start indexes
    new_starts = np.zeros(starts.size)
    for k in range(starts.size):
        start = starts[k]
        progress(start,
                 darray[0].size,
                 'Shifting starts',
                 step_number,
                 total_steps,
                 kind=kind)
        nan_start = nan_list_idx[nan_list_idx <= start][-1]
        max_temp_start = max_temp_list_idx[max_temp_list_idx <= start][-1]-1
        tsi_out_start = tsi_out_list_idx[tsi_out_list_idx <= start][-1]
        if k > 0:
            last_end = ends[k-1]
        else:
            last_end = 0
        #Initital temperature
        init_temp = darray[depth_index, start]
        init_temp_list = np.where(darray[depth_index, :start+1] < init_temp)[0]
        if init_temp_list.size > 0:
            init_temp_start = init_temp_list[-1]
        else:
            init_temp_start = 0
        new_start = max(nan_start,
                        max_temp_start,
                        tsi_out_start,
                        last_end,
                        init_temp_start)
        new_starts[k] = new_start
    progress(1,
             1,
             'Shifting starts',
             step_number,
             total_steps,
             kind=kind)
    return new_starts.astype(int)

def ends(starts, ends, darray,
         depth=25, num_max_right=60,
         step_number=4,
         total_steps=7,
         kind='bot'):
    """
    Shift end indexes to the right to get proper pulse start
    """
    #Index of relevant depth
    depth_index = np.where(darray.depth == depth)[0][0]
    #Where nans
    nan_list_idx = np.where(np.isnan(darray[depth_index]))[0]
    #Compute local right maximum
    shifted_darray = pd.DataFrame()
    for k in range(1, num_max_right):
        shifted_darray[k] = darray[depth_index].shift(time=k)-darray[depth_index]
    test_max_right = (shifted_darray < 0).sum(axis=1)
    max_right_idx = np.where(test_max_right == num_max_right-1)[0]
    #Where relevnt T is the maximum temp in depth
    max_temp_list_idx = np.where(darray[depth_index] == darray.max('depth'))[0]
    #Add last value
    last_idx = darray[0].size-1
    if last_idx not in nan_list_idx:
        nan_list_idx = np.insert(nan_list_idx,
                                 nan_list_idx.size,
                                 last_idx)
    if last_idx not in max_right_idx:
        max_right_idx = np.insert(max_right_idx,
                                  max_right_idx.size,
                                  last_idx)
    if last_idx not in max_temp_list_idx:
        max_temp_list_idx = np.insert(max_temp_list_idx,
                                      max_temp_list_idx.size,
                                      last_idx)
    #Create new end indexes array
    new_ends = np.zeros(ends.size)
    for k in range(starts.size):
        start = starts[k]
        end = ends[k]
        progress(start,
                 darray[0].size,
                 'Shifting ends',
                 step_number,
                 total_steps,
                 kind=kind)
        nan_end = nan_list_idx[nan_list_idx >= end][0]
        max_right_end = max_right_idx[max_right_idx >= end][0]
        max_temp_end = max_temp_list_idx[max_temp_list_idx >= end][0]
        #Initital temperature
        init_temp = darray[depth_index, start]
        init_temp_list = np.where(darray[depth_index, end:] > init_temp)[0]
        if init_temp_list.size > 0:
            init_temp_end = init_temp_list[0]+end
        else:
            init_temp_end = last_idx
        new_end = min(nan_end,
                      max_right_end,
                      init_temp_end,
                      max_temp_end)
        new_ends[k] = new_end
    progress(1,
             1,
             'Shifting ends',
             step_number,
             total_steps,
             kind=kind)
    return new_ends.astype(int)
