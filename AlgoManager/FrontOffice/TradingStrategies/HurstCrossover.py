from FrontOffice.backtesting import Backtest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from hurst import compute_Hc
from itertools import product
import warnings
warnings.filterwarnings("ignore")
plt.style.use("seaborn")

def hurst_indicator(series, window):
    
    if window < 100:
        raise ValueError('window must be greater or equal than 100')
        
    return series.rolling(window=window).apply(lambda x: compute_Hc(x)[0])
        

class HurstCrossover(Backtest):
    
    def __repr__(self):
        return "HurstCrossover(symbol = {}, start = {}, end = {})".format(self.symbol, self.start, self.end)
             
    def test_strategy(self, params):
        
        self.H_S = params[0]
        self.H_L = params[1]
        
        self.on_data(params = params)
        self.run_backtest()
        
        data = self.results.copy()
        data['creturns'] = data.returns.cumsum().apply(np.exp)
        data['cstrategy'] = data.strategy.cumsum().apply(np.exp)
        
        self.results = data
        self.print_performance()
        
    def on_data(self, params):
        
        data = self.data[['Close', 'returns']].copy()
        data['H_S'] = hurst_indicator(data.Close, params[0])
        data['H_L'] = hurst_indicator(data.Close, params[1])
        
        data.dropna(inplace=True)
        
        data['positions'] = 0
        
        cond = (data.H_S > .55) & (data.H_L > .55)
        cond1 = data.H_S > data.H_L
        cond2 = data.H_S < data.H_L
        
        data.loc[cond & cond1, 'positions'] = 1
        data.loc[cond & cond2, 'positions'] = -1
        
        self.results = data
    
    def optimize_strategy(self, H_S_range, H_L_range, metric = "multiple"):
        
        self.metric = metric
        
        if metric == 'multiple':
            
            performance_function = self.calculate_multiple
            
        elif metric == 'sharpe':
            
            performance_function = self.calculate_sharpe
            
        s_range = range(*H_S_range)
        l_range = range(*H_L_range)
        
        combinations = list(product(s_range, l_range))
        
        performance = []
        
        for comb in combinations:
            self.on_data(params=comb)
            self.run_backtest()
            performance.append(performance_function(self.results.strategy))
            
        self.performance_overview = pd.DataFrame(data = np.array(combinations), columns = ['small', 'large'])
        self.performance_overview['performance'] = performance
        self.find_best_strategy()
        
        
    def find_best_strategy(self):
        
        best = self.performance_overview.nlargest(1, 'performance')
        best_small = best.small.iloc[0]
        best_large = best.large.iloc[0]
        best_performance = best.performance.iloc[0]
        
        print('Returns perc. : {} | H_S = {} | H_L = {}'.format(best_performance, 
                                                                best_small,
                                                                best_large))
        
        self.test_performance(params = (best_small, best_large))
        
        
        
        