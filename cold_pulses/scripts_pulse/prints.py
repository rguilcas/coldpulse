# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:03:47 2020

@author: Robin
"""
import sys

def progress(t,duration,
             name,
             step_number,
             total_steps,
             kind = 'top'):
    """
    Print the progress of a loop
    """
    prog = t/duration*100
    if kind=='bot':
        intro = 'Bottom pulses step n°'
    elif kind=='top':
        intro = 'Top pulses step n°'
    sys.stdout.write('\r'+'%s%s/%s - %s ... %.02f'%\
        (intro,step_number,total_steps,name,prog) + r'%                           ')