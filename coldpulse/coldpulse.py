# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 09:08:42 2020

@author: rguil
"""
import os
from .inputs import prepare_darray
from .outputs import get_output, save_output


# =============================================================================
# Main functions
# =============================================================================
def upwelling_cold_pulses_detection(input_dir, ignore_double=True):
    process = True
    list_dir= os.listdir()
    if '%s_TSI_out'%input_dir in list_dir and ignore_double:
        process = False
    if not('%s_TSI_out'%input_dir in list_dir):
        os.mkdir('%s_TSI_out'%input_dir)
    if process:
        darray = prepare_darray(input_dir)
        df_output, ds_output, df_output_sub = get_output(darray, input_dir)
        save_output(df_output, 
                    df_output_sub,
                    ds_output,
                    input_dir,
                    dir_name='%s_TSI_out'%input_dir)

