from IPython.display import display, Markdown, Latex
import pandas as pd
from matplotlib import pyplot as plt
from analytics.time_series import get_frequency, convert_freq, logreturns
import numpy as np
from beautifultable import BeautifulTable
import analytics.basicstats as bs
import statsmodels.api as sm


rolling_period_weekly = 12
rolling_period_monthly = 12


class Performance_Report:
    
    def __init__(self, ts):
             
        self.ts = ts
        self.manager_name = 'Manager'
        self.product_name = 'Product'
        self.index_name = 'Index'
        self.as_of_date = str(ts.index[ts.shape[0] - 1])[0 : 10]
        self.freq = get_frequency(ts)
        self.manager_ret = ts.Manager
        self.index_ret = ts.Index
        
        self.cum_ret_manager = cum_return(ts.Manager)
        self.cum_ret_index = cum_return(ts.Index)
        self.date = pre_date(ts.index)
        
        self.manager_trailing_ret = trail_ret(ts.Manager)
        self.index_trailing_ret = trail_ret(ts.Index)
        
        self.calendar_ret = ts.resample('Y').apply(logreturns)
        
        self.manager_ann_ret = get_ann_ret(self.manager_ret, self.freq)
        self.index_ann_ret = get_ann_ret(self.index_ret, self.freq)
        self.manager_ann_std = get_ann_std(self.manager_ret, self.freq)
        self.index_ann_std = get_ann_std(self.index_ret, self.freq)
        
        self.manager_basic_stats = get_basic_stats(self.manager_ret)
        self.index_basic_stats = get_basic_stats(self.index_ret)
        self.list_basic_stats = ['Annualized Std', 'Sharpe ratio', 'Sortino ratio', 'Sortino Adj', 'Best Period', 'Worst Period',\
                                'Pct Up', 'Pct Down', 'Average Gain', 'Average Loss', 'Max Drawdown', 'VaR', 'VaR Adj']
        
        self.manager_relative_stats = get_relative_stats(self.manager_ret, self.index_ret, self.freq)
        self.list_relative_stats = ['Beta', 'R-squared', 'Tracking Error', 'Information ratio', 'Treynor ratio']
        
        self.manager_maxdd = get_maxdd(self.manager_ret)
        self.index_maxdd = get_maxdd(self.index_ret)
        
        self.rolling_stats = get_rolling_stats(self.manager_ret, self.index_ret, self.freq)
        
        if(self.freq == 'W'):
            self.rolling_period = rolling_period_weekly
            self.rolling_freq = '-week'
        elif(self.freq == 'M'):
            self.rolling_period = rolling_period_monthly
            self.rolling_freq = '-month'
        else:
            self.rolling_period = 1
            self.rolling_freq = 'NA'

        
        
def get_rolling_stats(ret_list_manager, ret_list_index, frequency):
    
    std_ser_manager = []
    std_ser_index = []
    beta_ser = []
    alpha_ser = []
    cum_alpha = 0
    
    if(frequency == 'W'):
        n_to_use = rolling_period_weekly
    if(frequency == 'M'):
        n_to_use = rolling_period_monthly
        
    for i in range(len(ret_list_manager) - n_to_use + 1):
        
        std_ser_manager.append(np.std(ret_list_manager[i : i + n_to_use]))
        std_ser_index.append(np.std(ret_list_index[i : i + n_to_use]))
        model = sm.OLS(ret_list_manager[i : i + n_to_use], ret_list_index[i : i + n_to_use], has_const = True)
        fit = model.fit()
        beta_ser.append(fit.params[0])
        cum_alpha = cum_alpha + ret_list_manager[i + n_to_use - 1] - ret_list_index[i + n_to_use - 1] * fit.params[0]
        alpha_ser.append(cum_alpha)
        
    return [std_ser_manager, std_ser_index, beta_ser, alpha_ser]
        
        
def get_maxdd(ret_list):    
    
    basicstats = bs.BasicStats(ret_list)
    output_list = list(basicstats.mdd_ser)
    output_list.insert(0, 0)
    
    return output_list
    
        
        

def get_relative_stats(ret_list_manager, ret_list_index, frequency):
    
    if(frequency == 'W'):
        factor = 52
    if(frequency == 'M'):
        factor = 12
    
    output_list = []
    diff = ret_list_manager - ret_list_index
    model = sm.OLS(ret_list_manager, ret_list_index, hasconst = True)
    fit = model.fit()
    output_list.append('{:.3}'.format(fit.params[0]))
    output_list.append('{:.1%}'.format(fit.rsquared))
    output_list.append('{:.2%}'.format(np.std(diff) * np.sqrt(factor)))
    output_list.append('{:.3}'.format(np.mean(diff) / np.std(diff) * np.sqrt(factor)))
    output_list.append('{:.3}'.format(np.mean(ret_list_manager) / fit.params[0] * factor))
    
    return output_list
        
    
def get_basic_stats(ret_list):
    
    output_list = []
    basicstats = bs.BasicStats(ret_list)
    output_list.append('{:.2%}'.format(basicstats.ann_std))
    output_list.append('{:.3}'.format(basicstats.sharpe))
    output_list.append('{:.3}'.format(basicstats.sortino))
    output_list.append('{:.3}'.format(basicstats.sortino_adj))
    output_list.append('{:.2%}'.format(basicstats.best))
    output_list.append('{:.2%}'.format(basicstats.worst))
    output_list.append('{:.2%}'.format(basicstats.pct_up))
    output_list.append('{:.2%}'.format(basicstats.pct_dn))
    output_list.append('{:.2%}'.format(basicstats.avg_gain))
    output_list.append('{:.2%}'.format(basicstats.avg_loss))
    output_list.append('{:.2%}'.format(basicstats.maxdd))
    output_list.append('{:.2%}'.format(basicstats.var))
    output_list.append('{:.2%}'.format(basicstats.var_adj))
    
    return output_list
    
    
def get_ann_std(ret_list, frequency):
    
    s = np.std(ret_list)
    if(frequency == 'W'):
        return s * np.sqrt(52)
    elif(frequency == 'M'):
        return s * np.sqrt(12)
    else:
        return 'NA'
    
    
def get_ann_ret(ret_list, frequency):
    
    n_period = len(ret_list)
    cumulative_return = cum_return(ret_list)[n_period]
    if(frequency == 'W'):
        return cumulative_return ** (52 / n_period) - 1
    elif(frequency == 'M'):
        return cumulative_return ** (12 / n_period) - 1
    else:
        return 'NA'
    
        
# Convert a return series into a cumulative return series
def cum_return(ret):
    
    cr = [1]
    len_of_ret = len(ret)  
    
    for i in range(len_of_ret):
        cr.append(cr[i] * (1 + ret[i]))   
        
    return cr

# Add one element to the beginning of date series
def pre_date(old_dt):
    
    new_dt = ['inception']
    len_of_dt = len(old_dt)   
    
    for i in range(len_of_dt):
        new_dt.append(str(old_dt[i])[0 : 10])   
        
    return new_dt

# Calculate trailing returns
def trail_ret(ret):
    
    monthly_ret = convert_freq(ret, 'M')
    length = len(monthly_ret)
    trail_ret_list = [monthly_ret[length - 1]]
    
    if(length >= 3):
        trail_ret_list.append(cum_return(monthly_ret[length - 3 : length])[3] - 1)
    else:
        trail_ret_list.append('NA')
    if(length >= 6):
        trail_ret_list.append(cum_return(monthly_ret[length - 6 : length])[6] - 1)
    else:
        trail_ret_list.append('NA')
    if(length >= 12):
        trail_ret_list.append(cum_return(monthly_ret[length - 12 : length])[12] - 1)
    else:
        trail_ret_list.append('NA')
    if(length >= 24):
        trail_ret_list.append(cum_return(monthly_ret[length - 24 : length])[24] - 1)
    else:
        trail_ret_list.append('NA')
    if(length >= 36):
        trail_ret_list.append(cum_return(monthly_ret[length - 36 : length])[36] - 1)
    else:
        trail_ret_list.append('NA')
    trail_ret_list.append(cum_return(monthly_ret)[length] - 1)
    
    return trail_ret_list


def as_percentage(data_list):
    
    for i in range(len(data_list)):
        if(isinstance(data_list[i], float)):
            data_list[i] = '{:.2%}'.format(data_list[i])
    return data_list



# Reading inputs from .csv file with first column as dates, second column as manager returns and third column as index returns
# All return numbers are shown as decimal numbers, so 1% is shown as 0.01

ts = pd.read_csv(r'data\manager.csv', parse_dates = ['Date'], index_col = ['Date'])
new_report = Performance_Report(ts)



# Below are the outputs in Markdown format

display(Markdown('## Manager Performance Report'))
print()
display(Markdown('#### Manager Name:  ' + new_report.manager_name))
display(Markdown('#### Benchmark:  ' + new_report.index_name))
display(Markdown('#### Performance as of:  ' + new_report.as_of_date))
display(Markdown('#### Contents:'))
display(Markdown('- Returns Chart\n- Trailing Period Returns\n- Calendar Year Returns\n- Risk Return Scatterplot\n\
- Risk Table\n- Drawdown Analysis\n- Rolling Standard Deviation\n- Rolling Beta\n- Cumulative Alpha'))

display(Markdown('#### 1. Returns Chart'))
plt.plot(new_report.date, new_report.cum_ret_manager)
plt.plot(new_report.date, new_report.cum_ret_index)
plt.title('Cumulative Return')
plt.xlabel('Time')
plt.ylabel('Growth of $1')
plt.xticks(new_report.date[::int(len(new_report.date) / 5)])
plt.legend([new_report.manager_name, new_report.index_name])

plt.show()

display(Markdown('#### 2. Trailing Period Returns'))
print()
new_table = BeautifulTable()
new_table.append_column('Trailing Period', ['1 Month', '3 Months', '6 Months', '1 Year', '2 Years', '3 Years', 'Since Inception'])
new_table.append_column(new_report.manager_name, as_percentage(new_report.manager_trailing_ret))
new_table.append_column(new_report.index_name, as_percentage(new_report.index_trailing_ret))

print(new_table)

display(Markdown('#### 3. Calendar Year Returns'))
print()

last_year = int(new_report.as_of_date[0:4])
n = len(new_report.calendar_ret)
index_list = range(last_year - n + 1, last_year + 1)
new_table = BeautifulTable()
new_table.append_column('Calendar Year', index_list)
new_table.append_column(new_report.manager_name, as_percentage(list(new_report.calendar_ret.Manager)))
new_table.append_column(new_report.index_name, as_percentage(list(new_report.calendar_ret.Index)))

print(new_table)

display(Markdown('#### 4. Risk Return Scatterplot'))
print()

plt.scatter(new_report.manager_ann_std, new_report.manager_ann_ret)
plt.scatter(new_report.index_ann_std, new_report.index_ann_ret)
plt.xlim(0,)
plt.hlines(0, xmin = 0, xmax = max(new_report.manager_ann_std, new_report.index_ann_std), linestyles = 'dashed', colors = '0.7')
sharpe1_x = np.linspace(0, max(new_report.manager_ann_std, new_report.index_ann_std))
sharpe1_y = sharpe1_x
plt.plot(sharpe1_x, sharpe1_y, color = '0.7', linestyle = 'dashed')
plt.title('Risk Return Plot')
plt.xlabel('Annualized Risk')
plt.ylabel('Annualized Return')
plt.legend(['Sharpe = 1', new_report.manager_name, new_report.index_name])

plt.show()

display(Markdown('#### 5. Risk Table'))
print()

new_table = BeautifulTable()
new_table.append_column('Stats', new_report.list_basic_stats)
new_table.append_column(new_report.manager_name, list(new_report.manager_basic_stats))
new_table.append_column(new_report.index_name, list(new_report.index_basic_stats))

print(new_table)
print()

new_table = BeautifulTable()
new_table.append_column('Stats', new_report.list_relative_stats)
new_table.append_column(new_report.manager_name, list(new_report.manager_relative_stats))

print(new_table)

display(Markdown('#### 6. Drawdown Analysis'))
print()

plt.plot(new_report.date, new_report.manager_maxdd)
plt.plot(new_report.date, new_report.index_maxdd)
plt.title('Underwater Curve')
plt.xlabel('Time')
plt.ylabel('Drawdown')
plt.xticks(new_report.date[::int(len(new_report.date) / 5)])
plt.legend([new_report.manager_name, new_report.index_name])

plt.show()

display(Markdown('#### 7. Rolling Standard Deviation'))
print()

plt.plot(new_report.date[new_report.rolling_period :], new_report.rolling_stats[0])
plt.plot(new_report.date[new_report.rolling_period :], new_report.rolling_stats[1])
plt.title('Rolling ' + str(new_report.rolling_period) + new_report.rolling_freq + ' Standard Deviation')
plt.xlabel('Time')
plt.ylabel('Standard Deviation')
plt.xticks(new_report.date[new_report.rolling_period : : int(len(new_report.date[new_report.rolling_period :]) / 5)])
plt.legend([new_report.manager_name, new_report.index_name])

plt.show()

display(Markdown('#### 8. Rolling Beta'))
print()

plt.plot(new_report.date[new_report.rolling_period :], new_report.rolling_stats[2])
plt.title('Rolling ' + str(new_report.rolling_period) + new_report.rolling_freq + ' Beta')
plt.xlabel('Time')
plt.ylabel('Beta')
plt.xticks(new_report.date[new_report.rolling_period : : int(len(new_report.date[new_report.rolling_period :]) / 5)])
plt.legend([new_report.manager_name])

plt.show()

display(Markdown('#### 9. Cumulative Alpha'))
print()

plt.plot(new_report.date[new_report.rolling_period :], new_report.rolling_stats[3])
plt.title('Cumulative Alpha')
plt.xlabel('Time')
plt.ylabel('Alpha')
plt.xticks(new_report.date[new_report.rolling_period : : int(len(new_report.date[new_report.rolling_period :]) / 5)])
plt.legend([new_report.manager_name])

plt.show()