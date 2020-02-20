# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:29:43 2020

@author: Robin
"""

file = open('config_file.txt')
data = file.read().splitlines()
data = [line.split(':') for line in data]

config_data = dict()
for k in [0,1,2,3,5,6,8,9]:
    config_data[data[k][0]] = data[k][1] 

depths_dic = dict()
for k in range(12,len(data)-1):
    depths_dic[data[k][0]] = int(data[k][1] )

config_data['depths'] = depths_dic
