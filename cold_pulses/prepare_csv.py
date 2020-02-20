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
import numpy as np
from cold_pulses.config_file import make_config_data


def prepare_csv():
    """
    This function turn several csv file into a unique multidimensional netcdf
    file
    """
    # Import configuration file data
    config_data = make_config_data('config_file.txt')
    depths = config_data['depths']
    input_folder = config_data['input_folder']
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
        return
    # If one of the csv files in the folder does not have a specified depth in
    # the config file, exit.
    for file in csv_files:
        if file not in depths.keys:
            print('Some or all files are incorrect or missing.')
            print('Please update the config_file.txt depths value.')
            return
    # Open and process file over which interpolation will be done
    time_file = pd.read_csv('%s/%s'%(input_folder, time_file_name))
    time_file.columns = ['time', 'temperature']
    time_file.index = pd.DatetimeIndex(time_file.time)
    # Create dataframe of all data in csv files
    data_dataframe = pd.DataFrame()
    for key in depths:
    # Open and process one file
        file = pd.read_csv('%s/%s'%(input_folder, key))
        print('%s loaded.'%key)
        file.columns = ['time', 'temperature']
        file.index = pd.DatetimeIndex(file.time)
    # If the file is the one over which we interpolate, add it directly to the
    # dataframe. If not, interpolate it first to the right sampling rate, and
    # add it to the dataframe
        if key != time_file_name:
            interpolated_data = np.interp(time_file.index,
                                          file.index,
                                          file.temperature,
                                          left=np.nan,
                                          right=np.nan)
            data_dataframe[depths[key]] = interpolated_data
        else:
            data_dataframe[depths[key]] = file.temperature
    # Sort depths values in decreasing order
    data_dataframe = data_dataframe.sort_index(axis=1, ascending=False)
    # Create an xarray DataArray from the pandas DataFrame
    data_darray = xr.DataArray(data_dataframe.values.T,
                               dims=['depth', 'time'],
                               coords={'depth':data_dataframe.columns,
                                       'time':data_dataframe.index})
    data_darray.name = 'temperature'
    # Save the dataarray as a netcf file
    data_darray.to_netcdf('%s/%s.nc'%(input_folder, name_nc_file))
      