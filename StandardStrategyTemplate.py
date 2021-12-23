from FrontOffice.backtesting import Backtest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from itertools import product
import warnings
warnings.filterwarnings("ignore")
plt.style.use("seaborn")


class NameTheStrategy(Backtest):
    
    def __repr__(self):
        return "NameTheStrategy(symbol = {}, start = {}, end = {})".format(self.symbol, self.start, self.end)
             
    def test_strategy(self, strategy_parameters):
        
        #call on data parameters and run backtest#
        
        self.on_data(strategy_parameters)
        self.run_backtest()
        
        #Store and show relevant data
        
        data = self.results.copy()
        data['creturns'] = data.returns.cumsum().apply(np.exp)
        data['cstrategy'] = data.strategy.cumsum().apply(np.exp)
        
        self.results = data
        self.print_performance()
    
    def on_data(self, strategy_parameters):
        
        #Prepare the Data#
        
        
        #Define Logic#
        
        
        #store it#
        self.results = data
    
    def optimize_strategy(self, SMA_S_range, SMA_M_range, SMA_L_range, metric = "multiple"):
        
        self.metric = metric
        
        if metric == 'multiple':
            
            performance_function = self.calculate_multiple
            
        elif metric == 'sharpe':
            
            performance_function = self.calculate_sharpe
            
        #Optimization Logic#
        
        #store logic results in 
        
        self.performance_overview = pd.DataFrame()
        
        #Finally call
        self.find_best_strategy()
        
        
    def find_best_strategy(self):
        
        best = self.performance_overview(1, 'performance')
        
        print('Returns perc. : {} | parameter1 = {} | parameter2 = {} | ...'.format())
        
        self.test_strategy(your_best_params)
        