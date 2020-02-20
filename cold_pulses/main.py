# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:34:45 2020

@author: Robin
"""
import os
import xarray as xr
from cold_pulses.detect_pulse import top_pulse_detect,bot_pulse_detect
from cold_pulses.config_config_file import input_name,output_name,output_dir,bot,top

import warnings
warnings.filterwarnings("ignore")

darray = xr.open_dataarray(input_name)
if bot or top:
    dir_name = '%s/%s_pulses_out'%(output_dir,output_name)
    os.mkdir(dir_name)
if bot:
    df_bot,ds_bot = bot_pulse_detect(darray)
    df_bot.to_csv('%s/%s_bot_stats.csv'%(dir_name,output_name))
if top:
    df_top,ds_top = top_pulse_detect(darray)
    df_top.to_csv('%s/%s_top_stats.csv'%(dir_name,output_name))
    
list_darray = []
if top and not bot:
    ds_top.to_netcdf('%s/%s_top_data.nc'%(dir_name,output_name))
if bot and not top:
    ds_bot.to_netcdf('%s/%s_bot_data.nc'%(dir_name,output_name))
if top and bot:
    ds = xr.Dataset()
    ds['temp'] = ds_top.temp
    ds['gamma_top'] = ds_top.gamma
    ds['pulse_temp_top'] = ds_top.pulse_temp
    ds['gamma_bot'] = ds_bot.gamma
    ds['pulse_temp_bot'] = ds_bot.pulse_temp
    ds.to_netcdf('%s/%s_all_data.nc'%(dir_name,output_name))
    