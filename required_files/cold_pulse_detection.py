# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:17:39 2020

@author: Robin
"""

#First in command prompt : pip install git+http://github.com/typhonier/cold_pulses

from cold_pulses.main import run
from cold_pulses.config_file import make_config_data
from cold_pulses.prepare_csv import prepare_csv
config_file = make_config_data('config_file.txt')
prepare_csv_test = config_file['prepare_csv']
if prepare_csv_test == 'True':
    prepare_csv()
run()

