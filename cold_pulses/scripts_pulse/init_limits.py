# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 14:14:51 2020

@author: Robin
"""
import numpy as np
import xarray as xr

def top(tsi, r_tsi, darray,
        depth=25):
    """
    tsi is a xarray dataarray of a temperature stratification index.
    r_tsi is an array of rolling daily TSI

    Returns two arrays with the initial starts and ends for possible top pulses
    """
    # Create a TSI time series where negative values of TSI are set to zero
    tsi_pos = xr.DataArray(np.copy(tsi),
                           dims=['time'],
                           coords={'time':tsi.time})
    tsi_pos[tsi_pos < 0] = 0
    # Create a rTSI time series where negative values of rTSI are set to zero
    r_tsi_pos = xr.DataArray(np.copy(r_tsi),
                             dims=['time'],
                             coords={'time':tsi.time})
    r_tsi_pos[r_tsi_pos < 0] = 0
    # Compute TSI anomaly by comparing positive TSI to positive rTSI
    tsi_pos_anomaly = tsi_pos - r_tsi_pos
    # Create a test to detect positive anomaly periods
    positive_anomaly = np.copy(tsi_pos_anomaly)
    positive_anomaly[positive_anomaly <= 0] = 0
    positive_anomaly[np.isnan(positive_anomaly)] = 0
    positive_anomaly[positive_anomaly > 0] = 1
    # Create a test to detect where the relevant depth shows the cooler
    # temperature
    min_temp = (darray.sel(depth=depth) == darray.min('depth'))\
                [:positive_anomaly.size]
    # Create a complete test to detect top pulse presence as a continuous
    # period of positive TSI anomaly and of minimum temperature
    top_pulse_presence = positive_anomaly * min_temp
    # Extract start and end indexes from the test time series
    starts = np.where(np.diff(top_pulse_presence) > 0)[0]
    ends = np.where(np.diff(top_pulse_presence) < 0)[0]+2
    # Add potential extreme indexes
    if starts[0] > ends[0]:
        starts = np.insert(starts, 0, 0)
    if starts[-1] > ends[-1]:
        ends = np.insert(ends, ends.size, tsi.size)
    return starts, ends


def bot(tsi, r_tsi, darray,
        depth=25):
    """
    theta is a xarray dataarray of a temperature stratification index.
    daily theta is an array of surface induced daily stratification

    Returns two arrays with the initial starts and ends for possible bot pulses
    """
    # Create a TSI time series where positive values of TSI are set to zero
    tsi_pos = xr.DataArray(np.copy(tsi),
                           dims=['time'],
                           coords={'time':tsi.time})
    tsi_pos[tsi_pos > 0] = 0
    # Create a rTSI time series where positive values of rTSI are set to zero
    r_tsi_pos = xr.DataArray(np.copy(r_tsi),
                             dims=['time'],
                             coords={'time':tsi.time})
    r_tsi_pos[r_tsi_pos > 0] = 0
    # Compute TSI anomaly by comparing positive TSI to positive rTSI
    tsi_pos_anomaly = tsi_pos - r_tsi_pos
    # Create a test to detect negative anomaly periods
    negative_anomaly = np.copy(tsi_pos_anomaly)
    negative_anomaly[negative_anomaly <= 0] = 0
    negative_anomaly[np.isnan(negative_anomaly)] = 0
    negative_anomaly[negative_anomaly > 0] = 1
    # Create a test to detect where the relevant depth shows the cooler
    # temperature
    min_temp = (darray.sel(depth=depth) == darray.min('depth'))\
                [:negative_anomaly.size]
    # Create a complete test to detect bottom pulse presence as a continuous
    # period of negative TSI anomaly and of minimum temperature
    bottom_pulse_presence = negative_anomaly * min_temp
    # Extract start and end indexes from the test time series
    starts = np.where(np.diff(bottom_pulse_presence) > 0)[0]
    ends = np.where(np.diff(bottom_pulse_presence) < 0)[0]+2
    # Add potential extreme indexes
    if starts[0] > ends[0]:
        starts = np.insert(starts, 0, 0)
    if starts[-1] > ends[-1]:
        ends = np.insert(ends, ends.size, tsi.size)
    return starts, ends
