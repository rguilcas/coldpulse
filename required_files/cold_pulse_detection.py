# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:17:39 2020

@author: Robin
"""

#First in command prompt : pip install git+http://github.com/typhonier/cold_pulses

import os
from cold_pulses.main import run
from cold_pulses.prepare_csv import prepare_csv

# =============================================================================
# INPUT DATA : change these fields to the ones in your case
# =============================================================================
# Directory where csv files are stored
INPUT_DIR = 'input_folder' 
# Choose types of algorithme : bot = True for bottom pulses top = True for top
# Both together are possible
BOT = True
TOP = True
# Do you want to prepare your csv files? i.e. turn them into a useable 
# netcdf file.
PREPARE_CSV = True
# If True you need to provide the following information.
# !!! Don't forget the .csv at the end of file names !!!
# List of file names:
FILE_NAMES = ['input_file_15m.csv',
              'input_file_25m.csv']
#4 List of file depths in the same order as they are in the file_names list
FILE_DEPTHS = [15,
               25]
# time_file_name is the file of which the time will be used for interpolation 
# of other files. 
TIME_FILE_NAME = 'input_file_15m.csv'


























# =============================================================================
# CREATE CONFIGURATION DATA : do not change this part
# =============================================================================

CONFIG_DATA = dict()
CONFIG_DATA['input_dir'] = '%s/%s'%('/'.join(os.getcwd().split('\\')),INPUT_DIR)
CONFIG_DATA['bot'] = BOT
CONFIG_DATA['top'] = TOP
CONFIG_DATA['prepare_csv'] = PREPARE_CSV 
if CONFIG_DATA['prepare_csv']:
    CONFIG_DATA['depths'] = dict()
    for k in range(len(FILE_NAMES)):
        CONFIG_DATA['depths'][FILE_NAMES[k]] = FILE_DEPTHS[k]
    CONFIG_DATA['time_file_name'] = TIME_FILE_NAME 
CONFIG_DATA['output_name'] = CONFIG_DATA['input_dir']
CONFIG_DATA['output_dir'] = CONFIG_DATA['input_dir']
CONFIG_DATA['name_nc_file'] = 'csv_prepared.nc'
CONFIG_DATA['input_name'] = CONFIG_DATA['input_dir']+'/csv_prepared.nc'    

# =============================================================================
# RUN ALGORITHM
# =============================================================================
if PREPARE_CSV == True:
    print('CSV files are being prepared ...')
    prepare_csv(CONFIG_DATA)
    print('NetCDF file is ready to be used.')
else:
    print('CSV files are already prepared.')
run(CONFIG_DATA)
