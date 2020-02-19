# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 21:13:19 2020

@author: Robin
"""
import numpy as np
import xarray as xr
import pandas as pd

def temperature_stratification_index(darray,dt,daily=True):#days
    """
    darray is a xarray dataarray of temperatures with 2 dimensions : depth and time
    
    Returns a xarray dataarray of the temperature anomaly index computed using
    Ladd and Stabbeno's stratification index routine
    """
    #Commpute temperature stratification index
    theta = ((darray-darray.mean('depth'))*darray.depth).mean('depth')
#    theta_corrected = theta-long_term_theta
    #Computes regular daily stratification variation induced by heatgin at the surface
    if daily:
        darray_h = darray.resample(time='h').median()
        where_nan = np.isnan(darray_h).sum(axis=0)
        where_nan = where_nan.where(where_nan==0,-1)
        where_nan = where_nan+1
        
        where_nan_diff = where_nan.diff('time')
        if(where_nan[0]==1):
            where_nan_diff[0]=1
        if(where_nan[-1]==1):
            where_nan_diff[-1]=-1
        
        starts = np.where(where_nan_diff>0)[0]
        ends = np.where(where_nan_diff<0)[0]
        
        theta_interpolated_full = xr.DataArray(np.nan*np.ones(darray_h.shape[1]),
                                                dims=['time'],
                                                coords = {'time':darray_h.time})
        for k in range(len(starts)):
            start = starts[k]
            end = ends[k]
            
            depth_data = []
            for depth in range(3):
                darray_depth = darray_h[:,start:end].isel(depth=depth)
                data = []
                hours = []
                start_hour = darray_depth.time.dt.hour.values[0]
                for hour in range(start_hour,start_hour+24):
                    if hour>23:
                        hour -= 24
                    data.append(darray_depth.where(darray_depth.time.dt.hour==hour).dropna('time').values)
                    hours.append(hour)
                sizes = []
                for d in data:
                    sizes.append(d.size)
                s = np.max(sizes)   
                new_data = []        
                for d in data:
                    if d.size < s:
                        new_data.append(np.insert(d,0,d[0]))
                    else:new_data.append(d)
                hour_data = pd.DataFrame(np.array(new_data).T)
                hours = []
                num_days_rolling = 60
                rolling_hourly = hour_data.rolling(num_days_rolling,center=True).median()
                rolling_hourly.iloc[0] = rolling_hourly.dropna().iloc[0]
                rolling_hourly.iloc[-1] = rolling_hourly.dropna().iloc[-1]
                hourly_series = rolling_hourly.interpolate().values.flatten()
                depth_data.append(hourly_series)
            hourly_darray = xr.DataArray(np.array(depth_data)[:,:end-start],
                                         dims=darray_h.dims,
                                         coords = darray_h[:,start:end].coords)
            hourly_theta = ((hourly_darray-hourly_darray.mean('depth'))*\
                             hourly_darray.depth).mean('depth')
            num_val_smooth = 3
            max_hourly_th = hourly_theta.rolling(time=num_val_smooth).max()
            max_hourly_th = max_hourly_th.where(max_hourly_th>0,0)
            min_hourly_th = hourly_theta.rolling(time=num_val_smooth).min()
            min_hourly_th = min_hourly_th.where(min_hourly_th<0,0)
            hourly_theta = max_hourly_th + min_hourly_th
            
            
            theta_interpolated_full[start:end] = hourly_theta
            
        daily_theta = theta_interpolated_full.interp(time=darray.time)
#    daily_theta_corrected = daily_theta-daily_theta.mean()
    #Interpolates daily stratification value to match darray timesteps
    
    
        return theta,daily_theta
    else:
        return theta
