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



class MACDCrossover(Backtest):
    
    def __repr__(self):
        return "NameTheStrategy(symbol = {}, start = {}, end = {})".format(self.symbol, self.start, self.end)
             
    def test_strategy(self, params):
        
        #call on data parameters and run backtest#
        
        self.EMA_line1 = params[0]
        self.EMA_line2 = params[1]
        self.EMA_signal = params[2]
        
        self.on_data(strategy_parameters)
        self.run_backtest()
        
        #Store and show relevant data
        
        data = self.results.copy()
        data['creturns'] = data.returns.cumsum().apply(np.exp)
        data['cstrategy'] = data.strategy.cumsum().apply(np.exp)
        
        self.results = data
        self.print_performance()
    
    def on_data(self, params):
        
        data = self.Data[['Close', 'return']]
        
        data = Indicator(data).MACD(ema_line_s = params[0], 
                                    ema_line_l = params[1], 
                                    ema_signal = params[2])
        
        data['position'] = 0
        
        cond1 = (data.MACD_signal > data.MACD_line) #& (data.MACD_hist)
        cond2 = (data.MACD_signal < data.MACD_line) #& (data.MACD_hist)
        
        
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
        