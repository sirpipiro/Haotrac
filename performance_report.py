# -*- coding: utf-8 -*-
from utils import cal_trailing_returns

class Performance_Report:
    
    def __init__(self, df, freq):
             
        self.fund_names = df.columns.values[:-1]
        self.benchmark_name = df.columns.values[-1]
        self.start_date = df.index.values[0]
        self.end_date = df.index.values[-1]
        
        self.frequency = freq
        self.cum_returns = (df + 1).cumprod()
        self.trail_returns = cal_trailing_returns(df, freq)