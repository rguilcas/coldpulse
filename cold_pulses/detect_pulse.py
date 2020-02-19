# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 20:49:26 2020

@author: Robin
"""

import xarray as xr
import seaborn as sns
import numpy as np

from scripts_pulse.temp_stratification_index import \
                    temperature_stratification_index
from scripts_pulse.init_start_end import init_top,init_bot
from scripts_pulse.filters import (filter_by_duration,
                                   filter_by_drop,
                                   filter_true_stratification,
                                   remove_overlap)
from scripts_pulse.shifts import shift_ends,shift_starts
from scripts_pulse.metrics import output

sns.set()
#darray = xr.open_dataarray('several_depth_data/palmyra_FR7_2012_2014.nc')
darray = xr.open_dataarray('several_depth_data/palmyra_N_2015.nc')
    
def bot_pulse_detect(darray):
    dt = darray.time.diff('time').values[0].astype('timedelta64[s]').astype(int)
    darray = darray.where(np.isnan(darray).sum('depth')==0,np.nan)
    depth = darray.depth.max()
    theta,daily_theta = temperature_stratification_index(darray,dt)
    starts,ends = init_bot(theta,daily_theta,darray,depth=depth)
    starts,ends = filter_by_duration(starts,ends)
    starts,ends = filter_by_drop(darray,starts,ends,
                                 depth=depth,kind='bot',
                                 step_number = 1,total_steps = 5)
    starts = shift_starts(starts,ends,darray,theta,
                          depth=depth,kind='bot',
                          step_number = 2,total_steps = 5)
    ends = shift_ends(starts,ends,darray,
                      depth=depth,kind='bot',
                      step_number = 3,total_steps = 5)
    starts,ends = filter_true_stratification(darray,starts,ends,dt,
                                             depth=depth,kind='bot',
                                             step_number=4, total_steps=5)
    #SHIFT START!!!
    starts,ends = remove_overlap(starts,ends)
    df_out,ds_out= output(darray,starts,ends,dt, 
                          depth=depth,kind='bot',
                          step_number = 5, total_steps = 5)
    return df_out,ds_out

def top_pulse_detect(darray):
    dt = darray.time.diff('time').values[0].astype('timedelta64[s]').astype(int)
    darray = darray.where(np.isnan(darray).sum('depth')==0,np.nan)
    depth = darray.depth.min()
    tsi,daily_tsi = temperature_stratification_index(darray,dt)
    starts,ends = init_top(tsi,daily_tsi)
    starts,ends = filter_by_duration(starts,ends)
    starts,ends = filter_by_drop(darray,starts,ends,
                                 depth=depth,kind='top',
                                 step_number = 1,total_steps = 5)
    starts = shift_starts(starts,ends,darray,tsi,
                          depth = depth,kind='top',
                          step_number = 2, total_steps = 5)
    ends = shift_ends(starts,ends,darray,
                      depth=depth,kind='top',
                      step_number = 3, total_steps = 5)
    starts,ends = filter_true_stratification(darray,starts,ends,dt,
                                             depth=depth,kind='top',
                                             step_number=4,total_steps = 5)
    df_out,ds_out= output(darray,starts,ends,dt, 
                          depth = depth, kind = 'top',
                          step_number = 5, total_steps = 5)
    return df_out,ds_out

