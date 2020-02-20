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
                    
def filter_by_duration(starts,ends,min_duration = 3):
    """
    starts and ends are np arrays representing the indexes of possible pulses
    min_duration is the minimum number of measurements that will be allowed
    between starts and ends
    
    Return 2 arrays starts and ends filtered by minimum duration
    """
    df = pd.DataFrame({'start':starts,
                       'end':ends})
    df['duration'] = df.end-df.start
    df_filtered = df.loc[df.duration >= min_duration]
    return df_filtered.start.values, df_filtered.end.values

def filter_by_drop(darray,starts,ends,
                   depth = 25,cut_off = .01,
                   step_number = 1,
                   total_steps = 7,
                   kind='bot'):
    """
    darray is an xarray dataaarray of the temperature
    starts and ends are np arrays representing the indexes of possible pulses
    cut_off is the minimum drop allowed at the depth chosen
    
    Returns starts and ends indexes filtered taking only those associated with 
    a drop in the depth desired.
    """
    df = pd.DataFrame({'start':starts,
                       'end':ends})
    all_drops = []
    for k in range(starts.size):
        start = starts[k]
        end = ends[k]
        progress(start,
                 darray[0].size,
                 'Filtering drops',
                 step_number,
                 total_steps,
                 kind=kind)
        drops = (darray[:,start]-darray[:,start:end]).max('time').values
        all_drops.append(drops)
        
    try:
        index_depth = np.where(darray.depth == depth)[0][0]
    except:
        print('No depth corresponding')
#        return
    
    all_drops = np.array(all_drops)
    df['drops'] = all_drops[:,index_depth]
    df_filtered = df.loc[df.drops>cut_off]
    progress(1,
             1,
             'Filtering drops',
             step_number,
             total_steps,
             kind=kind)
    return df_filtered.start.values, df_filtered.end.values


def filter_true_stratification(darray,starts,ends,dt,
                               depth = 25, min_theta = .04,
                               step_number = 2,
                               total_steps = 7,kind='bot'):
    """
    darray is an xarray dataaarray of the temperature
    starts and ends are np arrays representing the indexes of possible pulses
    
    Compute stratification index by keeping only the effects of one specific depth
    """
    #Creating copy of the darray file to create fake temperature profile sTSI
    darray_copy = xr.DataArray(np.copy(darray),
                             dims=['depth','time'],
                             coords={'depth':darray.depth,
                                     'time':darray.time})
    darray_copy[:] = np.nan
    length = darray.shape[1]
    
    try:
        index_depth = int(np.where(darray.depth == depth)[0][0])
    except:
        return('No depth corresponding')
        
    #Extract all irrelevant depths
    slicing = np.array([True]*darray.depth.size)
    slicing[index_depth]=False
    
    
    for k in range(starts.size):
        start = starts[k]
        end = ends[k]
        progress(start,
                 darray[0].size,
                 'Filtering specific TSI',
                 step_number,
                 total_steps,
                 kind=kind)
        #Initial values
        init_value = darray[index_depth,start].values
        #Linear interpolation between start and end
        interpolation = np.nan*np.zeros((darray_copy.depth.size-1,end-start+2))
        interpolation[:,0] = darray[index_depth,max(0,start-1)]
        interpolation[:,-1] = darray[index_depth,min(end,length-1)]
        df = pd.DataFrame(interpolation.transpose())
        interpolation = df.interpolate().values.transpose()[:,1:-1]
        interpolation = xr.DataArray(interpolation,
                                     dims = ['depth','time'],
                                     coords = {'depth':darray.depth[slicing],
                                               'time':darray_copy[slicing,start:end].time})
        #If interpolation is bigger than init value:init value        
        interpolation = interpolation.where(interpolation < init_value,init_value)
        #Ifi interpolation is bigger than sensors value, sensors valu
        interpolation = interpolation.where(interpolation < darray[slicing,start:end],
                                            darray[slicing,start:end])
        #If interpolation is smaller than relevant value:relevant value
        interpolation = interpolation.where(interpolation > darray[index_depth,start:end],
                                            darray[index_depth,start:end])
        
        darray_copy[slicing,start:end] = interpolation
        darray_copy[index_depth,start:end] = darray[index_depth,start:end]
    progress(1,
             1,
             'Filtering specific TSI',
             step_number,
             total_steps,
             kind=kind)
    
    theta = temperature_stratification_index(darray_copy,dt,daily = False)
    
#    Compute maximum stratification index for each possible pulse
    min_theta_list = []
    for k in range(starts.size):
        start = starts[k]
        end = ends[k]
        if kind=='top':
            min_strat = theta[start:end].max()
        elif kind=='bot':
            min_strat = theta[start:end].min()
        min_theta_list.append(min_strat.values)
    df = pd.DataFrame({'start':starts,
                       'end':ends,
                       'min_strat':min_theta_list})
    if kind=='bot':
        df_filtered = df.loc[df.min_strat < -min_theta]
    elif kind=='top':
        df_filtered = df.loc[df.min_strat > min_theta]
    return df_filtered.start.values,df_filtered.end.values
         
def remove_overlap(starts,ends):
    """
    starts and ends are np arrays representing the indexes of possible pulses
    
    Removes overlapping values of start and end to combine pulses
    Returns new arrays of starts and ends indexes
    """
    test = np.zeros(ends[-1])
    for k in range(starts.size):
        start=starts[k]
        end = ends[k]
        test[start:end]=1
    new_starts = np.where(np.diff(test)>0)[0]
    new_ends = np.where(np.diff(test)<0)[0]
    if test[0]==1:
        new_starts = np.insert(new_starts,0,0)
    if test[-1]==1:
        new_ends = np.insert(new_ends,new_ends.size,ends[-1])
    return new_starts, new_ends
