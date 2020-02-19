# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 14:14:51 2020

@author: Robin
"""
import numpy as np
import xarray as xr

def init_top(theta,daily_theta):
    """
    theta is a xarray dataarray of a temperature stratification index.
    daily theta is an array of surface induced daily stratification
    
    Returns two arrays with the initial starts and ends for possible top pulses
    """
    theta_pos = xr.DataArray(np.copy(theta),
                             dims=['time'],
                             coords={'time':theta.time})
    theta_pos[theta_pos < 0] = 0
    theta_pos_daily = xr.DataArray(np.copy(daily_theta),
                             dims=['time'],
                             coords={'time':theta.time})
    theta_pos_daily[theta_pos_daily < 0] = 0
    
    theta_less_daily = theta_pos-theta_pos_daily
    theta_less_daily[theta_less_daily < 0] = 0
    theta_less_daily[np.isnan(theta_less_daily)] = 0
    testtop = theta_less_daily
    testtop[testtop<=0]=0
    testtop[testtop>0]=1
    starts = np.where(np.diff(testtop)>0)[0]
    ends = np.where(np.diff(testtop)<0)[0]
    
    if starts[0] > ends[0]:
        starts = np.insert(starts,0,0)
    if starts[-1] > ends[-1]:
        ends = np.insert(ends,ends.size,theta.size)
    
    return starts,ends


def init_bot(theta,daily_theta,darray,depth=25):
    """
    theta is a xarray dataarray of a temperature stratification index.
    daily theta is an array of surface induced daily stratification
    
    Returns two arrays with the initial starts and ends for possible bot pulses
    """
    theta_neg = xr.DataArray(np.copy(theta),
                             dims=['time'],
                             coords={'time':theta.time})
    theta_neg[theta_neg > 0] = 0
    theta_neg_daily = xr.DataArray(np.copy(daily_theta),
                             dims=['time'],
                             coords={'time':theta.time})
    theta_neg_daily[theta_neg_daily > 0] = 0
    
    theta_less_daily = theta_neg-theta_neg_daily
    theta_less_daily[theta_less_daily > 0] = 0
    theta_less_daily[np.isnan(theta_less_daily)] = 0
    testbot = -theta_less_daily
    testbot[testbot<=0]=0
    testbot[testbot>0]=1
    test_min_temp = (darray.sel(depth=depth)==darray.min('depth'))[:-1]
    test_final = testbot*test_min_temp
    starts = np.where(np.diff(test_final)>0)[0]
    ends = np.where(np.diff(test_final)<0)[0]
    
    if starts[0] > ends[0]:
        starts = np.insert(starts,0,0)
    if starts[-1] > ends[-1]:
        ends = np.insert(ends,ends.size,theta.size)
    
    return starts,ends

