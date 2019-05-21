# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:38:36 2019

@author: Leo

This provides various utilities which can be used in other projects.
"""
import pandas as pd

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

# Helper function to generate a string of fund names, seperated with comma followed by space
def get_name_string(fund_names):
    
    name_string=str()
    for i, item in enumerate(fund_names):
        if(i>0):
            name_string+=', '
        name_string+=item
        
    return name_string

"""
Helper function to generate trailing period returns.
Trailing periods include 1 month, 3 months, 6 months, 1 year, 2 years, 3 years, 5 years and since inception.
For weekly data, we simplify and assume 4 weeks == 1 month and 52 weeks == 1 year.   
"""

def cal_trailing_returns(ret_df, frequency = 'w'):

    assert frequency == 'w' or frequency == 'm'
    
    if(frequency == 'w'):
        factors = [4, 12, 24, 52, 156, 260]
    else:
        factors = [1, 3, 6, 12, 36, 60]
        
    length_of_returns = ret_df.shape[0]
    out_df = pd.DataFrame(index = ['1 month', '3 months', '6 months', '1 year', '3 years', '5 years', 'since inception'], 
                          columns = ret_df.columns.values)
    
    for column in ret_df.columns:
        
        for i in range(6):
        
            if(factors[i] <= length_of_returns):
                out_df[column][i] = (ret_df[column].tail(factors[i]) + 1).prod() - 1
            else:
                out_df[column][i] = 'NA'
        
        out_df[column][6] = (ret_df[column] + 1).prod() - 1
  
    return out_df