# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 12:01:44 2020

@author: rguil
"""

import cold_pulses.pulse_detection as detect
import os

list_dirs = os.listdir()
list_dirs.remove('run_TSI.py')
list_dirs.remove('NCEP-GODAS_ocean-temp_1980-2020.nc')

for dir_name in list_dirs:
    if dir_name[-3:]!='out':
        print(dir_name)
        detect.upwelling_cold_pulses_detection(dir_name,auto_in=True,ignore_double=True)
