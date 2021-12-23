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
        
        data = self.data[['Close','returns']].copy()
        
        data = Indicator(data).BollingerBands(sma = params[0], 
                                             scaling_factor = params[1])
        
        data['distance'] = data.Close - data.middleBand
        
        data.dropna(inplace = True)
        
        data['positions'] = 0
        
        cond1 = data.Close > data.upperBand 
        cond2 = data.Close < data.lowerBand 
        cond3 = data.distance * data.distance.shift(1) < 0
        
        data.loc[cond1, 'positions'] = 1
        data.loc[cond2, 'positions'] = -1
        data.loc[cond3, 'positions'] = 0
        
        self.results = data
    
    def optimize_strategy(self, SMA_range, DEV_range, metric = "multiple"):
        
        self.metric = metric
        
        if metric == 'multiple':
            
            performance_function = self.calculate_multiple
            
        elif metric == 'sharpe':
            
            performance_function = self.calculate_sharpe
            
        sma_range = range(*SMA_range)
        dev_range = range(*DEV_range)
        
        combinations = list(product(sma_range,dev_range))
        
        performance = []
        
        for comb in combinations:
            self.on_data(params=comb)
            self.run_backtest()
            performance.append(performance_function(self.results.strategy))
        
        
        self.performance_overview = pd.DataFrame(data=np.array(combinations), columns = ['sma', 'scaling_factor'])
        self.performance_overview['performance'] = performance
        
        self.find_best_strategy()
        
        
    def find_best_strategy(self):
        
        best = self.performance_overview.nlargest(1, 'performance')
        best_sma = best.sma.iloc[0]
        best_factor = best.scaling_factor.iloc[0]
        best_performance = best.performance.iloc[0]
        
        print('Returns perc. : {} | SMA = {} | Scaling Factor = {}'.format(best_performance, best_sma, best_factor))
        
        self.test_strategy(params = (best_sma, best_factor))
        