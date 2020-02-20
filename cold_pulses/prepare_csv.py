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
config_data = make_config_data('config_file.txt')
def prepare_csv():  
  depths = config_data['depths']
  input_folder = config_data['input_folder']
  time_file_name = config_data['time_file_name']
  name_nc_file = config_data['name_nc_file']

  LIST_FILES = os.listdir(input_folder)
  CSV_FILES = [k for k in LIST_FILES if k[-3:]=='csv']
  if len(CSV_FILES) != len(depths.keys()):
      print('Wrong depths in config_file.py.')
      print('Please indicate one depth for each csv file in the input folder.')
  else:
      TIME_FILE = pd.read_csv('%s/%s'%(input_folder, time_file_name))
      TIME_FILE.columns = ['time', 'temperature']
      TIME_FILE.index = pd.DatetimeIndex(TIME_FILE.time)
      DATA_DATAFRAME = pd.DataFrame()
      for key in depths:
          file = pd.read_csv('%s/%s'%(input_folder, key))
          print('%s loaded.')
          file.columns = ['time', 'temperature']
          file.index = pd.DatetimeIndex(file.time)
          if key != time_file_name:
              interpolated_data = np.interp(TIME_FILE.index,
                                            file.index,
                                            file.temperature,
                                            left=np.nan,
                                            right=np.nan)
              DATA_DATAFRAME[depths[key]] = interpolated_data
          else:
              DATA_DATAFRAME[depths[key]] = file.temperature
      DATA_DATAFRAME = DATA_DATAFRAME.sort_index(axis=1, ascending=False)
      DATA_DARRAY = xr.DataArray(DATA_DATAFRAME.values.T,
                                 dims=['depth', 'time'],
                                 coords={'depth':DATA_DATAFRAME.columns,
                                         'time':DATA_DATAFRAME.index})
      DATA_DARRAY.name = 'temperature'
      DATA_DARRAY.to_netcdf('%s/%s.nc'%(input_folder, name_nc_file))

def reload_config_file():
  from cold_pulses.config_file import config_data
  