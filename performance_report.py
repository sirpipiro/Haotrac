class Performance_Report:
    
    def __init__(self, df):
             
        self.fund_names=df.columns.values[:-1]
        self.benchmark_name=df.columns.values[-1]
        self.start_date=df.index.values[0]
        self.end_date=df.index.values[-1]
        self.cum_returns=(df+1).cumprod()