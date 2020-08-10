# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 12:01:44 2020

@author: rguil
"""

import cold_pulses.pulse_detection as detect
import os

list_dirs = os.listdir()
if 'NCEP-GODAS_ocean-temp_1980-2020.nc' not in list_dirs:
    print('NCEP-GODAS climatology file, please download it first.')
    print('If you have downloaded it, move it to the current working directory.')
    print("If it is in the current directory, rename it it 'NCEP-GODAS_ocean-temp_1980-2020.nc'")

else:
    list_dirs.remove('processing_TSI.py')
    list_dirs.remove('NCEP-GODAS_ocean-temp_1980-2020.nc')

    for dir_name in list_dirs:
        if dir_name[-3:]!='out' and dir_name[0] != '.' and dir_name!='desktop.ini':
            print(dir_name)
            detect.upwelling_cold_pulses_detection(dir_name,auto_in=True,ignore_double=True)
            
