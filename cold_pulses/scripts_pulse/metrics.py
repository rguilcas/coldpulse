# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:55:47 2020

@author: Robin
"""
import numpy as np
import xarray as xr
import pandas as pd
from cold_pulses.scripts_pulse.prints import progress

def output(darray, starts, ends, dt,
           step_number=4,
           total_steps=7,
           depth=25,
           kind='bot'):
    """
    Create output files from start and end indexes of pulses
    """
    # Create empty time series that will contain instantaneous degree cooling
    # hours
    darray_dch = xr.DataArray(np.nan*np.zeros(darray.shape),
                              dims=darray.dims,
                              coords=darray.coords)
    # Create empty time series that will contain pulses temperature
    darray_pulse_temp = xr.DataArray(np.nan*np.zeros(darray.shape),
                                     dims=darray.dims,
                                     coords=darray.coords)
    # Create empty list that will contain all individual pulses information
    data_df_out = []
    for k in range(starts.size):
    # Extract start and end indexes
        start = starts[k]
        end = ends[k]
    # Print progress
        progress(start,
                 darray[0].size,
                 'Preparing output files',
                 step_number,
                 total_steps,
                 kind=kind)
    # Compute degree cooling hours and maximum drops
        dch_instant, drops = get_gamma(start, end, darray, dt,
                                       depth=depth)
    # Update DCH time series
        darray_dch[:, start:end] = dch_instant
    # Update pulses temp time series
        darray_pulse_temp[:, start:end] = darray[:, start:end]
    # Compute integrated DCH
        dch_integr = dch_instant.sum(axis=1)
    # Compute duration in minutes
        start_time = darray.time[start].values
        duration = (darray.time[end].values - start_time).\
                    astype('timedelta64[m]').astype(int)
    # Extract initial temperature
        temp_init = darray[:, start].values
    # Create data line for individual pulse
        data = [start_time, duration]+\
                list(dch_integr)+\
                list(drops)+\
                list(temp_init)+\
                [start, end]
    # Update pulses list information
        data_df_out.append(data)
    progress(1,
             1,
             'Preparing output files',
             step_number,
             total_steps,
             kind=kind)
    # Create output dataset
    ds = xr.Dataset()
    # Update additional information to the dataarrays
    darray.attrs['long_name'] = 'Temperature'
    darray.attrs['unit'] = '°C'
    darray_dch.attrs['long_name'] = 'Degree Cooling Hours'
    darray_dch.attrs['unit'] = '°C.h'
    darray_pulse_temp.attrs['long_name'] = 'Pulse temperature'
    darray_pulse_temp.attrs['unit'] = '°C'
    # Add dataarrays to output dataset
    ds['temp'] = darray
    ds['dch'] = darray_dch
    ds['pulse_temp'] = darray_pulse_temp
    # Create output dataframe
    df = pd.DataFrame(data_df_out)
    df.columns = ['start_time', 'duration']+\
                 ['gamma%s'%k for k in list(darray.depth.values)]+\
                 ['drop%s'%k for k in list(darray.depth.values)]+\
                 ['temp_init%s'%k for k in list(darray.depth.values)]+\
                 ['start', 'end']
    df.index = pd.DatetimeIndex(df.start_time)
    return df[df.columns[1:]], ds

def get_gamma(start, end, darray, dt,
              depth=25):
    # Extract depth index and temperature series at that depth
    index_depth = np.where(darray.depth == depth)[0][0]
    extracted_darray = darray[index_depth, start:end]
    # Compute temperature gradient at relevent depth
    diff_extracted_darray = extracted_darray.diff('time')
    # Initialise start and end of sub pulses
    moving_start_list = np.where(diff_extracted_darray < 0)[0]
    if moving_start_list.size > 0:
        moving_start = moving_start_list[0]
        moving_end_list = np.where(extracted_darray[moving_start+1:] \
                                       > extracted_darray[moving_start])[0]
        if moving_end_list.size > 0:
            moving_end = moving_start + 1 + moving_end_list[0]
        else:
            moving_end = end
        # Create list of sub pulses starts and ends
        start_depth = [moving_start]
        end_depth = [moving_end]
    else:
        moving_end = end
        start_depth = []
        end_depth = []
    # Go through the time series to find subpulses
    while moving_end < end:
        moving_start_list = np.where(diff_extracted_darray[moving_end:])[0]
        if moving_start_list.size > 0:
            moving_start = moving_end + moving_start_list[0]
            moving_end_list = np.where(extracted_darray[moving_start+1:] \
                                   > extracted_darray[moving_start])[0]
            if moving_end_list.size > 0:
                moving_end = moving_start + 1 + moving_end_list[0]
            else:
                moving_end = end
            start_depth.append(moving_start)
            end_depth.append(moving_end)
        else:
            moving_end = end
    # Prepare empty time series to compute degree cooling seconds for relevant
    # depth
    dcs_relevant = np.zeros(extracted_darray.size)
    for k in range(len(start_depth)):
    # Extract start and end indexes for each subpulse
        start_sub = start_depth[k]
        end_sub = end_depth[k]
    # Compute DCS
        dcs_relevant[start_sub:end_sub] = \
            extracted_darray[start_sub]-extracted_darray[start_sub:end_sub]
    # Prepare the computation of DCS for irrelevant depths
    slicing = [True]*darray.depth.size
    slicing[index_depth] = False
    darray_irrelevant = darray[slicing, start:end]
    start_irrelevant_list_all = []
    end_irrelevant_list_all = []
    for k in range(darray_irrelevant.shape[0]):
    # Create a list that will contain subpulse starts and ends for each depth
        start_irrelevant_list = []
        end_irrelevant_list = []
    # Extract temperature data
        extracted_darray = darray_irrelevant[k]
    # Find all subpulses and add their start and end indexes to the lists
        end_loop = False
        forcing_start = False
        moving_start_list = np.where(diff_extracted_darray < 0)[0]
        if moving_start_list.size > 0:
            moving_start = moving_start_list[0]
            moving_start = np.where(diff_extracted_darray < 0)[0][0]
            moving_end_list = np.where(extracted_darray[moving_start+1:] \
                                      > extracted_darray[moving_start])[0]
            if moving_end_list.size > 0:
                moving_end = moving_start + 1 + moving_end_list[0]
            else:
                moving_end += 1
                end_loop = True
            if not end_loop:
                start_irrelevant_list = [moving_start]
                end_irrelevant_list = [moving_end]
        else:
            moving_end = end
            start_irrelevant_list = []
            end_irrelevant_list = []
        
        while moving_end < (end-start) and moving_start < end-start:
            moving_start_list = np.where(diff_extracted_darray[moving_end:])[0]
            if moving_start_list.size > 0:
                if not forcing_start:
                    moving_start = moving_end + moving_start_list[0]
                moving_end_list = \
                    np.where(diff_extracted_darray[moving_end:])[0]
                if moving_end_list.size > 0:
                    moving_end = moving_start + 1 + moving_end_list[0]
                    forcing_start = False
                    end_loop = False
                else:
                    moving_start += 1
                    forcing_start = True
                    end_loop = True
                if not end_loop:
                    start_irrelevant_list.append(moving_start)
                    end_irrelevant_list.append(moving_end)
            else:
                moving_end = end
            
        start_irrelevant_list_all.append(start_irrelevant_list)
        end_irrelevant_list_all.append(end_irrelevant_list)
    #
    dcs_irrelevant = np.zeros((darray.depth.size-1, extracted_darray.size))
    for i in range(darray.depth.size-1):
        # Compute DCS
        extracted_darray = darray[slicing][i, start:end]
        start_irrelevant_list = start_irrelevant_list_all[i]
        end_irrelevant_list = end_irrelevant_list_all[i]
        for k in range(len(start_irrelevant_list)):
            start_sub = start_irrelevant_list[k]
            end_sub = end_irrelevant_list[k]
            dcs_irrelevant[i, start_sub:end_sub] = \
                extracted_darray[start_sub]-extracted_darray[start_sub:end_sub]
    # Create full DCS array
    dcs_tot = np.zeros((darray.depth.size, end-start))
    # Update for relevant depth
    dcs_tot[index_depth] = dcs_relevant
    # Update for irrevelant depths
    dcs_tot[slicing] = dcs_irrelevant
    max_drops = dcs_tot.max(axis=1)
    dcs_tot = dcs_tot*dt
    #Convert dcs to dch
    dch_tot = dcs_tot/3600
    return dch_tot,max_drops
