# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:29:43 2020

@author: Robin
"""

input_name = 'several_depth_data/kingman2.nc'
output_name = 'kingman2'
output_dir = 'several_depth_data'
input_folder = 'W'

bot = True
top = True

depths = {'-162.075_5.870_4.9_PAL_1851_2012-05-15_2012-09-28.csv':5,
          '-162.075_5.870_10.7_PAL_1852_2012-05-15_2012-09-28.csv':10,
          '-162.075_5.870_19.5_PAL_1854_2012-05-15_2012-09-28.csv':20}

time_file_name = '-162.075_5.870_4.9_PAL_1851_2012-05-15_2012-09-28.csv'
name_nc_file = 'palmyra_E_12_15'