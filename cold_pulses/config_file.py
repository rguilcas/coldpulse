# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:29:43 2020

@author: Robin
"""
import os
from cold_pulse_detection import input_data
def make_config_data(file):
    """
    Import configuration file as a dictionnary
    """
    # Open config_file
    file = open(file)
    # Extract data
    data = file.read().splitlines()
    data = [line.split(':') for line in data]
    # Get current directory
    current_dir = '\\'.join(os.getcwd().split('\\'))
    # Create dict object and add all info to it
    config_data = dict()
    for k in range(5):
        # If directory (line of the file) add working directory to the path
        #if k in [0]:
        #    config_data[data[k][0]] = '%s/%s'%(current_dir, data[k][1])
        #else:
        config_data[data[k][0]] = data[k][1]
    # Create a dict file for different depth levels and files names
    config_data['input_name']=config_data['input_dir']+'/csv_prepared.nc'    
    config_data['output_name']=config_data['input_dir']
    config_data['output_dir']=config_data['input_dir']
    config_data['name_nc_file']='csv_prepared.nc'
    config_data['input_folder']=config_data['input_dir']
        
    depths_dic = dict()
    for k in range(7, len(data)):
        depths_dic[data[k][0]] = int(data[k][1])
    # Add depths info to the config_data dict
    config_data['depths'] = depths_dic
    return config_data
