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


class APOCrossover(Backtest):
    
    def __repr__(self):
        return "NameTheStrategy(symbol = {}, start = {}, end = {})".format(self.symbol, self.start, self.end)
             
    def test_strategy(self, params):
        
        self.EMA_S = params[0]
        self.EMA_L = params[1]
         
        
        self.on_data(params)
        self.run_backtest()
        
        
        data = self.results.copy()
        data['creturns'] = data.returns.cumsum().apply(np.exp)
        data['cstrategy'] = data.strategy.cumsum().apply(np.exp)
        
        self.results = data
        self.print_performance()
    
    def on_data(self, params):
        
        data = self.data[['Close','returns']].copy()
        
        data = Indicator(data).APO(params[0], params[1])
        
        data.dropna(inplace = True)
        
        
        data['positions'] = 0
        
        cond1 = data.APO > 0
        cond2 = data.APO < 0
        
        data.loc[cond1, 'positions'] = 1
        data.loc[cond2, 'positions'] = -1
        
        #store it#
        self.results = data
    
    def optimize_strategy(self, EMA_S_range, EMA_L_range, metric = "multiple"):
        
        self.metric = metric
        
        if metric == 'multiple':
            
            performance_function = self.calculate_multiple
            
        elif metric == 'sharpe':
            
            performance_function = self.calculate_sharpe
            
        #Optimization Logic#
        
        ema_s_range = range(*EMA_S_range)
        ema_l_range = range(*EMA_L_range)
        
        combinations = list(product(ema_s_range, ema_l_range))
        
        performance = []
        
        for comb in combinations:
            
            self.on_data(params = comb)
            self.run_backtest()
            performance.append(performance_function(self.results.strategy))
        
        
        self.performance_overview = pd.DataFrame(data = np.array(combinations), columns = ['ema_s', 'ema_l'])
        self.performance_overview['performance'] = performance
        
        self.find_best_strategy()
        
        
    def find_best_strategy(self):
        
        best = self.performance_overview.nlargest(1, 'performance')
        
        best_ema_s = best.ema_s.iloc[0]
        best_ema_l = best.ema_l.iloc[0]
        best_performance = best.performance.iloc[0]
        
        print('Returns perc. : {} | EMA_S = {} | EMA_L= {} | ...'.format(best_performance, best_ema_s, best_ema_l))
        
        self.test_strategy(params = (best_ema_s, best_ema_l))
        