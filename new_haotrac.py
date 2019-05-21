""" 
This is a re-write for Haotrac, my precious legacy from good days at Hillview Capital Advisors.
It leverages the reportlab library to generate pdf directly while the old R codes had to use the markdown language.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 #595.27, 841.89

from performance_report import Performance_Report
from utils import mask_chart_index, get_name_string


def get_cum_ret_chart(cum_returns):
    
    with sns.axes_style("darkgrid"):
        
        fig, ax = plt.subplots(figsize=(10,7))
        for column in cum_returns.columns:
            ax.plot(cum_returns[column])
        ax.set_title('Cumulative Returns')
        ax.grid(axis='x')
        ax.set_xlabel('Date')
        ax.set_ylabel('Growth of $1')
        ax.set_xticklabels(mask_chart_index(cum_returns.index, 6, 2))
        ax.legend()
    
    plt.savefig('./inputs/cum_returns_chart.jpg')
    
    return

def draw_table(my_canvas, my_df, x, y):
    
    nrows, ncolumns = my_df.shape
    xt = x + 110
    yt = y
    for j in range(ncolumns):
        my_canvas.drawString(xt, yt, my_df.columns[j])
        xt = xt + 70

    yt = y - 40
    for i in range(nrows):
        xt = x
        my_canvas.drawString(xt, yt, my_df.index[i])
        xt = xt + 40
        for j in range(ncolumns):
            xt = xt + 70
            if(type(my_df.values[i, j]) == np.float64):
                my_canvas.drawString(xt, yt, '%.1f' % (my_df.values[i, j] * 100))
            else:
                my_canvas.drawString(xt, yt, my_df.values[i, j])
           
        yt = yt - 20
    return



def get_haotrac_report(my_df, freq):

    my_report=Performance_Report(my_df, freq)
    get_cum_ret_chart(my_report.cum_returns)

    """
    Define format specifications of the report.
    """
    x0=50
    y0=720
    w0=400 #Default width of text blocks
    h0=25 #Space between lines

    fontz_title=20
    fontz_body=12

    my_canvas=canvas.Canvas('./paper.pdf', pagesize=A4)

    # Cover
    my_canvas.setFontSize(fontz_title)
    my_canvas.drawCentredString(300, 570, 'Fund Performance Report')
    
    my_canvas.setFontSize(fontz_body)
    my_canvas.drawCentredString(300, 500, 'Fund Names: ' + get_name_string(my_report.fund_names))
    my_canvas.drawCentredString(300, 480, 'Benchmark Name: ' + my_report.benchmark_name)
    my_canvas.drawCentredString(300, 460, 'Start Date: ' + str(my_report.start_date)[0:10])
    my_canvas.drawCentredString(300, 440, 'End Date: ' + str(my_report.end_date)[0:10])
    my_canvas.drawCentredString(300, 380, 'Contents:')
    my_canvas.drawCentredString(300, 330, 'Cumulative Returns')
    my_canvas.drawCentredString(300, 310, 'Trailing Returns')
    my_canvas.drawCentredString(300, 290, 'Calendar Year Returns')
    my_canvas.drawCentredString(300, 270, 'Risk Return Scatterplot')
    my_canvas.drawCentredString(300, 250, 'Risk Table')
    my_canvas.drawCentredString(300, 230, 'Drawdown Analysis')
    my_canvas.drawCentredString(300, 210, 'Rolling Volatility')
    my_canvas.drawCentredString(300, 190, 'Rolling Beta')
    
    my_canvas.drawImage('./inputs/Qiyi logo.jpg', 225, 600, width=150, preserveAspectRatio=True)    
    my_canvas.showPage()
    
    # Page 1
    my_canvas.setFontSize(fontz_title)
    my_canvas.drawString(x0, y0, '1. Cumulative Returns')
    my_canvas.drawString(x0, y0 - 370, '2. Trailing Period Returns')
    
    my_canvas.setFontSize(fontz_body)
    draw_table(my_canvas, my_report.trail_returns, x0 + 30, y0 - 410)
    
    my_canvas.drawImage('./inputs/cum_returns_chart.jpg', x0, y0 - 410, width=400, preserveAspectRatio=True)  
    my_canvas.showPage()
    
    my_canvas.save()


my_df = pd.read_csv('./data/manager.csv', index_col = 'Date', parse_dates = True)
get_haotrac_report(my_df, 'w')


