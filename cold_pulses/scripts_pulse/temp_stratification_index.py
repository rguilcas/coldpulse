# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 21:13:19 2020

@author: Robin
"""
import numpy as np
import xarray as xr
import pandas as pd

def temperature_stratification_index(darray,
                                     daily=True, num_days_rolling=60):#days
    """
    darray is a xarray dataarray of temperatures with 2 dimensions : depth and time

    Returns a xarray dataarray of the temperature anomaly index computed using
    Ladd and Stabbeno's stratification index routine
    """
    #Compute TSI
    tsi = ((darray-darray.mean('depth'))*darray.depth).mean('depth')
    if daily:
    # Compute rTSI
    # Resample temperature data to get hourly means
        darray_h = darray.resample(time='h').median()
    # Fond where nan values are in the time series
        where_nan = np.isnan(darray_h).sum(axis=0)
        where_nan = where_nan.where(where_nan == 0, -1)
        where_nan = where_nan+1
    # Extract start and end of continuous no nan values
        if where_nan.size > 0:
            where_nan_diff = where_nan.diff('time')
            if where_nan[0] == 1:
                where_nan_diff[0] = 1
            if where_nan[-1] == 1:
                where_nan_diff[-1] = -1
            starts = np.where(where_nan_diff > 0)[0]
            ends = np.where(where_nan_diff < 0)[0]
        else:
            starts = np.array([0])
            ends = np.array([tsi.size-1])
    # Create a new time series to interpolate rTSI values
        tsi_interpolated_full = xr.DataArray(np.nan*np.ones(darray_h.shape[1]),
                                             dims=['time'],
                                             coords={'time':darray_h.time})
        for k in range(starts.size):
    # For each continuous no nan time series, extract start and end indexes
            start = starts[k]
            end = ends[k]
            depth_data = []
            for depth in range(darray.depth.size):
    # For each depth, extract the temperature
                darray_depth = darray_h[:, start:end].isel(depth=depth)
                data = []
                hours = []
    # Extract the first hour of the day that is in the series
                start_hour = darray_depth.time.dt.hour.values[0]
                for hour in range(start_hour, start_hour+24):
    # For each hour, create a time series of hourly temperature at this hour
                    if hour > 23:
                        hour -= 24
                    data.append(darray_depth.\
                                where(darray_depth.time.dt.hour == hour).\
                                dropna('time').values)
                    hours.append(hour)
    # Compute hour time series size to make them all the same size
                sizes = []
                for data_line in data:
                    sizes.append(data_line.size)
                max_size = np.max(sizes)
                new_data = []
                for data_line in data:
                    if data_line.size < max_size:
                        new_data.append(np.insert(data_line, 0, data_line[0]))
                    else:
                        new_data.append(data_line)
    # Create dataframe from hour time series
                hour_data = pd.DataFrame(np.array(new_data).T)
                hours = []
    # Create a rolling average of hour time series during num_days_rolling
                rolling_hourly = hour_data.rolling\
                                (num_days_rolling, center=True).median()
    # Fll in missing values induced by rolling mean
                rolling_hourly.iloc[0] = rolling_hourly.dropna().iloc[0]
                rolling_hourly.iloc[-1] = rolling_hourly.dropna().iloc[-1]
                hourly_series = rolling_hourly.interpolate().values.flatten()
                depth_data.append(hourly_series)
    # Create a new complete time series that will contain rolling daily temp
    # series
            hourly_darray = xr.DataArray(np.array(depth_data)[:, :end-start],
                                         dims=darray_h.dims,
                                         coords=darray_h[:, start:end].coords)
    # Compute rTSI
            r_tsi = ((hourly_darray-hourly_darray.mean('depth'))*\
                             hourly_darray.depth).mean('depth')
    # Smoothing procedure
            num_val_smooth = 3
            max_r_tsi = r_tsi.rolling(time=num_val_smooth).max()
            max_r_tsi = max_r_tsi.where(max_r_tsi > 0, 0)
            min_r_tsi = r_tsi.rolling(time=num_val_smooth).min()
            min_r_tsi = min_r_tsi.where(min_r_tsi < 0, 0)
            r_tsi = max_r_tsi + min_r_tsi
            tsi_interpolated_full[start:end] = r_tsi
    # Get final rTSI
        r_tsi = tsi_interpolated_full.interp(time=darray.time)
        return tsi, r_tsi

    return tsi
