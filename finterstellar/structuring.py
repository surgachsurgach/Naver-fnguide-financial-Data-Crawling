import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates


class Structure:
    
    def __init__(self):
        plt.style.use('fivethirtyeight')

        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['axes.grid'] = True
        
        plt.rcParams['lines.linewidth'] = 1.5
        plt.rcParams['grid.linestyle'] = '--'
        plt.rcParams['grid.alpha'] = 0.7
        plt.rcParams['lines.antialiased'] = True
        
        plt.rcParams['figure.figsize'] = [10.0, 10.0]
        plt.rcParams['figure.dpi'] = 96
        plt.rcParams['savefig.dpi'] = 150

        plt.rcParams['font.size'] = 15
        plt.rcParams['legend.fontsize'] = 'small'
        plt.rcParams['figure.titlesize'] = 'medium'
        

    def value_at_expiry(self, x, **y):
        s = pd.Series(0 for _ in range(len(x)))
        for key, value in y.items():
            s = s + pd.Series(value)
        return (s)
        
        
        
