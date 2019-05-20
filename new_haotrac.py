""" 
This is a re-write for Haotrac, my precious legacy from good days at Hillview Capital Advisors.
It leverages the reportlab library to generate pdf directly while the old R codes had to use the markdown language.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 #595.27, 841.89

from performance_report import Performance_Report
from utils import mask_chart_index

def get_name_string(fund_names):
    
    name_string=str()
    for i, item in enumerate(fund_names):
        if(i>0):
            name_string+=', '
        name_string+=item
        
    return name_string

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

my_df=pd.read_csv('./data/manager.csv', index_col='Date')

def get_haotrac_report(my_df):

    my_report=Performance_Report(my_df)
    get_cum_ret_chart(my_report.cum_returns)

    """
    Define format specifications of the report.
    """
    x0=50
    y0=760
    w0=400 #Default width of text blocks
    h0=25 #Space between lines

    fontz_title=20
    fontz_body=12

    my_canvas=canvas.Canvas('./paper.pdf', pagesize=A4)

    # Cover
    my_canvas.setFontSize(fontz_title)
    my_canvas.drawCentredString(300, 570, 'Fund Performance Report')
    
    my_canvas.setFontSize(fontz_body)
    my_canvas.drawCentredString(300, 500, 'Fund Names: '+get_name_string(my_report.fund_names))
    my_canvas.drawCentredString(300, 480, 'Benchmark Name: '+my_report.benchmark_name)
    my_canvas.drawCentredString(300, 460, 'Start Date: '+my_report.start_date)
    my_canvas.drawCentredString(300, 440, 'End Date: '+my_report.end_date)
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
    
    my_canvas.drawImage('./inputs/cum_returns_chart.jpg', x0, 350, width=400, preserveAspectRatio=True)  
    my_canvas.showPage()
    
    my_canvas.save()



get_haotrac_report(my_df)


