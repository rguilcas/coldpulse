# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 13:36:37 2020

@author: Robin
"""

import numpy as np
import pandas as pd
import scipy.spatial as sp
def convex_hull_pulse(temp):
    data = np.array([np.arange(temp.size),np.copy(temp.values)]).T
    hull = sp.ConvexHull(data)
    vertices = np.tile(hull.vertices,2)
    test = np.copy(vertices)
    test[test>0] = 1
    test[test<0] = 0
    
    test = np.diff(vertices) < 0
    dift = np.diff(1*test)
    
    starts = np.where(dift>0)[0]
    ends = np.where(dift<0)[0]
    
    if test[0]:
        starts = np.insert(starts, 0, 0)
    if test[-1]:
        ends = np.insert(ends, ends.size, test.size-1)
    
    duration = ends-starts
    
    max_i = np.argmax(duration)
    start = starts[max_i]+1
    end = ends[max_i]+2
    outbound = vertices[start:end][::-1]
    new_temp = pd.Series(np.copy(temp))
    for index in new_temp.index:
        if index not in outbound:
            new_temp.iloc[index] = np.nan
    convex_hull = new_temp.interpolate()
    return convex_hull