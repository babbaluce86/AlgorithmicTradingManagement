from FrontOffice.backtesting import Backtest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from itertools import product
import warnings
warnings.filterwarnings("ignore")
plt.style.use("seaborn")

def BollingerIndicator(data, window, scaling_factor=2.5):
    
    middleBand = data.rolling(window=window).mean()
    upperBand = middleBand + scaling_factor * (data - middleBand).std()
    lowerBand = middleBand - scaling_factor * (data - middleBand).std()
    
    bbands = middleBand.to_frame(f'SMA{window}').join(upperBand.to_frame('upperBand')).join(lowerBand.to_frame('lowerBand'))
    
    return bbands

class TurtleBollinger(Backtest):
    
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
        
        self.scaling_factor = 2.5
        
        data = self.data[['Close','returns']].copy()
        data['high'] = BollingerIndicator(data.Close, window = params).upperBand
        data['low'] = BollingerIndicator(data.Close, window = params).lowerBand
        data['avg'] = data.Close.rolling(window=params).mean()
        
        data.dropna(inplace = True)
        
        data['positions'] = 0
        
        cond1 = (data.Close > data.high) & (data.Close > data.avg)
        cond2 = (data.Close < data.low) & (data.Close < data.avg)
        
        data.loc[cond1, 'positions'] = -1
        data.loc[cond2, 'positions'] = 1
        
        self.results = data
    
    def optimize_strategy(self, SMA_range, metric = "multiple"):
        
        self.metric = metric
        
        if metric == 'multiple':
            
            performance_function = self.calculate_multiple
            
        elif metric == 'sharpe':
            
            performance_function = self.calculate_sharpe
            
        sma_range = range(SMA_range[0], SMA_range[1])
        #scaling_range = range(*scaling_factor_range)
        
        #combinations = list(product(sma_range, scaling_range))
        
        performance = []
        
        for comb in sma_range:
            self.on_data(params=comb)
            self.run_backtest()
            performance.append(performance_function(self.results.strategy))
        
        
        self.performance_overview = pd.DataFrame(data=np.array(sma_range), columns = ['sma'])
        self.performance_overview['performance'] = performance
        
        self.find_best_strategy()
        
        
    def find_best_strategy(self):
        
        best = self.performance_overview.nlargest(1, 'performance')
        best_sma = best.sma.iloc[0]
        #best_factor = best.scaling_factor.iloc[0]
        best_performance = best.performance.iloc[0]
        
        print('Returns perc. : {} | SMA = {} | Factor = {}'.format(best_performance, best_sma, self.scaling_factor))
        
        self.test_strategy(params = best_sma)
        