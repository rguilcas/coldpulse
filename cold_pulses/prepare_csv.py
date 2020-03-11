# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 14:28:25 2020

@author: Robin

This file transforms csv files into a useable xarray DataArray for cold pulse
detections.
CSV files need to be written in two columns : time and temperature
"""

import os
import xarray as xr
import pandas as pd


def prepare_csv(config_data):
    """
    This function turn several csv file into a unique multidimensional netcdf
    file
    """
    # Import configuration file data
    depths = config_data['depths']
    input_folder = config_data['input_dir']
    time_file_name = config_data['time_file_name']
    name_nc_file = config_data['name_nc_file']
    list_files = os.listdir(input_folder)
    # Extract csv files from the files in the directory
    csv_files = [k for k in list_files if k[-3:] == 'csv']
    # If the number of files indicated in the config file is not the same as
    # the number of csv files in the folder, exit
    if len(csv_files) != len(depths.keys()):
        print('Wrong depths in config_file.py.')
        print('Please indicate one depth for each csv file in the input folder.')
        return False
    # If one of the csv files in the folder does not have a specified depth in
    # the config file, exit.
    for file in csv_files:
        if file not in depths.keys():
            print('Some or all files are incorrect or missing.')
            print('Please update the config_file.txt depths value.')
            return False
    # Open and process file over which interpolation will be done
    time_file = pd.read_csv('%s/%s'%(input_folder, time_file_name))
    time_file = time_file[time_file.columns[-2:]]
    time_file = time_file.sort_index()
    time_file.columns = ['time', 'temperature']
    time_file.index = pd.DatetimeIndex(time_file.time)
    ds_time = xr.DataArray(time_file.temperature.sort_index())
    # Create dataframe of all data in csv files
    list_ds_file = []
    for key in depths:
    # Open and process one file
        file = pd.read_csv('%s/%s'%(input_folder, key))
        file = file[file.columns[-2:]]
        print('%s loaded.'%key)
        file = file.sort_index()
        file.columns = ['time', 'temperature']
        file.index = pd.DatetimeIndex(file.time)
        ds_file = xr.DataArray(file.temperature.sort_index())
        
        interp_ds_file = ds_file.interp(time=ds_time.time)
        interp_ds_file['depth'] = depths[key]
        list_ds_file.append(interp_ds_file)
    # Create an xarray DataArray from the list of interpolated data
    data_darray = xr.concat(list_ds_file,'depth')
    data_darray.name = 'temperature'
    # Save the dataarray as a netcf file
    data_darray.to_netcdf('%s/%s'%(input_folder, name_nc_file))
    return True
