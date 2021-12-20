from FrontOffice.backtesting import Backtest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from itertools import product
import warnings
warnings.filterwarnings("ignore")
plt.style.use("seaborn")


class DoubleCrossover(Backtest):
    
    def __repr__(self):
        return "DoubleCrossover(symbol = {}, start = {}, end = {})".format(self.symbol, self.start, self.end)
             
    def test_strategy(self, smas):
        
        self.SMA_S = smas[0]
        self.SMA_L = smas[1]
        
        self.on_data(smas = smas)
        self.run_backtest()
        
        data = self.results.copy()
        
        data['creturns'] = data.returns.cumsum().apply(np.exp) 
        data['cstrategy'] = data.strategy.cumsum().apply(np.exp)
        
        self.results = data
        self.print_performance()
    
    def on_data(self, smas):
        
        data = self.data[['Close', 'returns']].copy()
        data['SMA_S'] = data.Close.rolling(window=smas[0]).mean()
        data['SMA_L'] = data.Close.rolling(window=smas[1]).mean()
        
        data['positions'] = 0
        
        cond1 = data.SMA_S > data.SMA_L 
        cond2 = data.SMA_S < data.SMA_L
        
        data.loc[cond1, 'positions'] = 1
        data.loc[cond2, 'positions'] = -1
        
        self.results = data
    
    def optimize_strategy(self, SMA_S_range, SMA_L_range, metric = "multiple"):
        
        self.metric = metric
        
        if self.metric == 'multiple':
            performance_metric = self.calculate_multiple
        
        elif self.metric == 'sharpe':
            percormance_metric = self.calculate_sharpe
            
        s_range = range(*SMA_S_range)
        l_range = range(*SMA_L_range)
        
        combinations = list(product(s_range, l_range))
        
        performance = []
        
        for comb in combinations:
            self.on_data(smas = comb)
            self.run_backtest()
            performance.append(performance_metric(self.results.strategy))
            
        self.performance_overview = pd.DataFrame(data = np.array(combinations), columns = ['SMA_S', 'SMA_L'])
        self.performance_overview['performance'] = performance
        
        self.find_best_strategy()
            
        
    def find_best_strategy(self):
        
        best = self.performance_overview.nlargest(1, 'performance')
        best_short = best.SMA_S.iloc[0]
        best_large = best.SMA_L.iloc[0]
        best_performance = best.performance.iloc[0]
        
        print('Return perc. {} | SMA_S = {} | SMA_L = {}'.format(best_performance, 
                                                                  best_short, 
                                                                  best_large))
        
        self.test_strategy(smas = (best_short, best_large))