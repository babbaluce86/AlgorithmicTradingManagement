from AlgorithmicTradingManagement.AlgoManager.FrontOffice.backtesting import Backtest
from AlgorithmicTradingManagement.AlgoManager.FrontOffice.Indicator import Indicator
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from itertools import product
import warnings
warnings.filterwarnings("ignore")
plt.style.use("seaborn")


class Turtle(Backtest):
    
    def __repr__(self):
        return "Turtle(symbol = {}, start = {}, end = {})".format(self.symbol, self.start, self.end)
             
    def test_strategy(self, params):
        
        #call on data parameters and run backtest#
        
        self.on_data(params)
        self.run_backtest()
        
        #Store and show relevant data
        
        data = self.results.copy()
        data['creturns'] = data.returns.cumsum().apply(np.exp)
        data['cstrategy'] = data.strategy.cumsum().apply(np.exp)
        
        self.results = data
        self.print_performance()
    
    def on_data(self, params):
        
        #Prepare the Data#
        
        data = self.data[['Close','returns']].copy()
        data['high'] = data.Close.shift(1).rolling(window=params).max()
        data['low'] = data.Close.shift(1).rolling(window=params).min()
        data['avg'] = data.Close.shift(1).rolling(window=params).mean()
        
        data.dropna(inplace = True)
        
        data['positions'] = 0
        
        cond1 = (data.Close > data.high) & (data.Close > data.avg)
        cond2 = (data.Close < data.low) & (data.Close < data.avg)
        
        data.loc[cond1, 'positions'] = -1
        data.loc[cond2, 'positions'] = 1
        
        self.results = data
    
    def optimize_strategy(self, params, metric = "multiple"):
        
        self.metric = metric
        
        if metric == 'multiple':
            
            performance_function = self.calculate_multiple
            
        elif metric == 'sharpe':
            
            performance_function = self.calculate_sharpe
            
        parameters = range(*params)
        
        performance = []
        
        for param in parameters:
            self.on_data(params=param)
            self.run_backtest()
            performance.append(performance_function(self.results.strategy))
        
        
        self.performance_overview = pd.DataFrame(data=np.array(parameters), columns = ['sma'])
        self.performance_overview['performance'] = performance
        
        self.find_best_strategy()
        
        
    def find_best_strategy(self):
        
        best = self.performance_overview.nlargest(1, 'performance')
        best_param = best.sma.iloc[0]
        best_performance = best.performance.iloc[0]
        
        print('Returns perc. : {} | SMA = {}'.format(best_performance, best_param))
        
        self.test_strategy(params = best_param)
        