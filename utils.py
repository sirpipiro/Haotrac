# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:38:36 2019

@author: Leo

This provides various utilities which can be used in other projects.
"""

# Helper function to generate better organized tick labels for matplotlib/seaborn charts.
def mask_chart_index(chart_index, num_ticks, start = 0):
    
    len_index = len(chart_index)
    size_mask = round(len_index / num_ticks)
    
    new_index = []
    count = start
    
    for index in chart_index:
        
        count = count + 1
        if(count == size_mask):
            new_index.append(index)
            count = 0
        else:
            new_index.append('')
    
    return new_index