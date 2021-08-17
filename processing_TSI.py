# -*- coding: utf-8 -*-
from coldpulse import coldpulse

list_input_dir = ['run']
for input_dir in list_input_dir:
    coldpulse.upwelling_cold_pulses_detection(input_dir)
