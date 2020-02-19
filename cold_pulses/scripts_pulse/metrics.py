# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:55:47 2020

@author: Robin
"""
import numpy as np
import xarray as xr
import pandas as pd
from scripts_pulse.prints import progress

def output(darray, starts, ends, dt,
           step_number=4,
           total_steps=7,
           depth=25,
           kind='bot'):
    da_gamma = xr.DataArray(np.nan*np.zeros(darray.shape),
                            dims=darray.dims,
                            coords=darray.coords)
    da_pulse_temp = xr.DataArray(np.nan*np.zeros(darray.shape),
                                 dims=darray.dims,
                                 coords=darray.coords)
    data_df_out = []
    for k in range(starts.size):
        start = starts[k]
        end = ends[k]
        progress(start,
                 darray[0].size,
                 'Preparing output files',
                 step_number,
                 total_steps,
                 kind=kind)
        gamma,drops = get_gamma(start, end, darray, dt,
                                depth=depth)
        da_gamma[:, start:end] = gamma
        da_pulse_temp[:, start:end] = darray[:, start:end]
        gamma_integr = gamma.sum(axis=1)
        start_time = darray.time[start].values
        duration = (darray.time[end].values - start_time).\
                astype('timedelta64[m]').astype(int)
        temp_init = darray[:, start].values
        data = [start_time, duration]+\
                list(gamma_integr)+\
                list(drops)+\
                list(temp_init)+\
                [start, end]
        data_df_out.append(data)
    progress(1,
             1,
             'Preparing output files',
             step_number,
             total_steps,
             kind=kind)
    ds = xr.Dataset()
    ds['temp'] = darray
    ds['gamma'] = da_gamma
    ds['pulse_temp'] = da_pulse_temp
    df = pd.DataFrame(data_df_out)
    df.columns = ['start_time', 'duration']+\
                 ['gamma%s'%k for k in list(darray.depth.values)]+\
                 ['drop%s'%k for k in list(darray.depth.values)]+\
                 ['temp_init%s'%k for k in list(darray.depth.values)]+\
                 ['start', 'end']
    df.index = pd.DatetimeIndex(df.start_time)
    return df, ds
 
def get_gamma(start, end, darray, dt,
              depth = 25):
    index_depth = np.where(darray.depth == depth)[0][0]
    extracted_darray = darray[index_depth, start:end]
    diff_extracted_darray = extracted_darray.diff('time')
    moving_start = np.where(diff_extracted_darray<0)[0][0]
    moving_end_list = np.where(extracted_darray[moving_start+1:] \
                                   > extracted_darray[moving_start])[0]
    if moving_end_list.size > 0:
        moving_end = moving_start + 1 + moving_end_list[0]
    else:
        moving_end = end
    start_depth = [moving_start]
    end_depth = [moving_end]
    while moving_end<end:
        moving_start_list = np.where(diff_extracted_darray[moving_end:])[0]
        if moving_start_list.size > 0:
            moving_start = moving_end + moving_start[0]
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
        
    gamma_deep = np.zeros(extracted_darray.size)
    for k in range(len(start_depth)):
        start_sub = start_depth[k]
        end_sub = end_depth[k]
        gamma_deep[start_sub:end_sub] = \
            extracted_darray[start_sub]-extracted_darray[start_sub:end_sub]
    
    slicing = [True]*darray.depth.size
    slicing[index_depth] = False

    no_deep_darray = darray[slicing,start:end]   
    start_shall_all=[]
    end_shall_all = []
    for k in range(no_deep_darray.shape[0]):
        start_shall = []
        end_shall = []
        extracted_darray = no_deep_darray[k]
        end_loop =  False
        forcing_start=False
        moving_start_list = np.where(diff_extracted_darray<0)[0]
        if moving_start_list.size > 0:
            moving_start = moving_start[0]
            moving_start = np.where(diff_extracted_darray<0)[0][0]
            moving_end_list = np.where(extracted_darray[moving_start+1:] \
                                      > extracted_darray[moving_start])[0]
            if moving_end_list.size > 0:
                moving_end =  moving_start + 1 + moving_end_list[0]
            else:
                moving_end +=1
                end_loop = True
        else:
            moving_end = end
        
        if not end_loop:
            start_shall = [moving_start]
            end_shall = [moving_end]
        while moving_end<(end-start) and moving_start<end-start:
            moving_start_list = np.where(diff_extracted_darray[moving_end:])[0]
            if moving_start_list.size > 0:
                if not forcing_start:
                    moving_start = moving_end + moving_start_list[0]
                moving_end_list = \
                    np.where(diff_extracted_darray[moving_end:])[0]
                if moving_end_list.size > 0:
                    moving_end = moving_start + 1 + moving_end_list[0]
                    forcing_start=False
                    end_loop=False
                else:
                    moving_start += 1
                    forcing_start=True
                    end_loop = True
                if not end_loop:
                    start_shall.append(moving_start)
                    end_shall.append(moving_end)
            else:
                moving_end = end
                
        start_shall_all.append(start_shall)
        end_shall_all.append(end_shall)
        
            
    gamma_shall = np.zeros((darray.depth.size-1,extracted_darray.size))
    for i in range(darray.depth.size-1):
        extracted_darray =  darray[slicing][i,start:end]
        start_shall = start_shall_all[i]
        end_shall = end_shall_all[i]
        for k in range(len(start_shall)):
            start_sub = start_shall[k]
            end_sub = end_shall[k]
            gamma_shall[i,start_sub:end_sub] = \
                extracted_darray[start_sub]-extracted_darray[start_sub:end_sub]
    gamma_tot = np.zeros((darray.depth.size,end-start))
    gamma_tot[index_depth] = gamma_deep
    gamma_tot[slicing] = gamma_shall
    max_drops = gamma_tot.max(axis = 1)
    gamma_tot = gamma_tot*dt
    return gamma_tot,max_drops