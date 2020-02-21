# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:34:45 2020

@author: Robin
"""
import os
import warnings
import xarray as xr
from cold_pulses.detect_pulse import top_pulse_detect, bot_pulse_detect
from cold_pulses.config_file import make_config_data

warnings.filterwarnings("ignore")

def run():
    """
    Main script that should be used to detect cold pulses.
    """
    # load config file info
    config_data = make_config_data('config_file.txt')
    input_name = config_data['input_name']
    output_name = config_data['output_name']
    output_dir = config_data['output_dir']
    bot = config_data['bot']
    top = config_data['top']
    # open netcdf file previously created by processing csv files
    darray = xr.open_dataarray(input_name)
    # If top or bot are selected, we will compute pulses, and therefore
    # create a new outup directory
    if bot or top:
        dir_name = '%s/%s_pulses_out'%(output_dir, output_name)
        if os.path.isdir(dir_name):
            existing_dir = input('This output dir already exists, do you want'\
                                +' to continue? It might erase previous outputs.'\
                                +'(y/n)')
        else:
            os.mkdir(dir_name)
    # If top or bot are selected, we compute pulses using detection algorithms
    # in detect_pulses
    if existing_dir == 'y':
        if bot:
            df_bot, ds_bot = bot_pulse_detect(darray)
            df_bot.to_csv('%s/%s_bot_stats.csv'%(dir_name, output_name))
        if top:
            df_top, ds_top = top_pulse_detect(darray)
            df_top.to_csv('%s/%s_top_stats.csv'%(dir_name, output_name))
        # If only top or bot is selected, we save the output of the relevant
        # detection script as a netcdf file
        if top and not bot:
            ds_top.to_netcdf('%s/%s_top_data.nc'%(dir_name, output_name))
        if bot and not top:
            ds_bot.to_netcdf('%s/%s_bot_data.nc'%(dir_name, output_name))
        # If both top and bot are selected, we create a new combined output file
        # with data from the bot and top scripts outputs and save it as a netcdf
        # file
        if top and bot:
            output_dataset = xr.Dataset()
            output_dataset['temp'] = ds_top.temp
            output_dataset['dch_top'] = ds_top.dch
            output_dataset['pulse_temp_top'] = ds_top.pulse_temp
            output_dataset['dch_bot'] = ds_bot.dch
            output_dataset['pulse_temp_bot'] = ds_bot.pulse_temp
            output_dataset.to_netcdf('%s/%s_all_data.nc'%(dir_name, output_name))
            