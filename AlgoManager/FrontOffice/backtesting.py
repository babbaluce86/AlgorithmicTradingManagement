from abc import ABCMeta, abstractmethod
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


class Backtest(object):
    
    '''This is a vectorized backtesting class, it provides a simple, fast and efficient code,
       be aware that in this backtesting style there are some drawbacks, it is indeed difficult to test path
       dependednt and recursive strategies. Nevertheless this can provide a fast engine to screen strategies.'''
    
    __metaclass__ = ABCMeta
    
    def __init__(self, symbol, start, end, tc, market = 'crypto', filepath=None, yahoo=None):
        
        
        self.filepath = filepath
        self.yahoo = yahoo
        self.symbol = symbol
        self.start = start
        self.end = end
        self.tc = tc
        self.market = market
        
        if self.market == 'crypto':
            self.total_days = 365.25
            
        elif self.market == 'stock':
            self.total_days = 252
        
        self.results = None
        self.get_data()
        
        self.tp_year = (self.data.Close.count() / ((self.data.index[-1] - self.data.index[0]).days / self.total_days))
        
    def get_data(self):
        
        if self.filepath:
            
            raw = pd.read_csv(self.filepath, parse_dates = ['Date'], index_col = 'Date')[['Close', 'Volume']]
            raw.index = pd.to_datetime(raw.index, utc = True)
            raw['returns'] = np.log(raw.Close/raw.Close.shift(1))
            
        elif self.yahoo:
            
            raw = yf.download(str(self.symbol), start='2020-01-01', end='2021-12-17', interval = '1h')[['Close', 'Volume']]
            raw.index.name = 'Date'
            raw.index = pd.to_datetime(raw.index).tz_convert(None)
            raw.index = pd.Series(raw.index).dt.floor('H')
            raw['returns'] = np.log(raw.Close/raw.Close.shift(1))
        
        self.data = raw[self.start : self.end]
        
        
    @abstractmethod
    def test_strategy(self):
        raise NotImplementedError("Should implement trigger_signal()")
    
    @abstractmethod
    def on_data(self):
        raise NotImplementedError("Should implement on_data()")
        
    def run_backtest(self):
        ''' Runs the strategy backtest.
        '''    
        data = self.results.copy()
        data["strategy"] = data["positions"].shift(1) * data["returns"]
        data["trades"] = data.positions.diff().fillna(0).abs()
        data.strategy = data.strategy + data.trades * self.tc
        
        self.results = data
        
    def plot_results(self):
        
        if self.results is None:
            print('Run test_strategy first')
        
        else:
            title = '{} | TC = {}'.format(self.symbol, self.tc)
            self.results[['creturns','cstrategy']].plot(figsize = (16,9), title = title)
        
    @abstractmethod
    def optimize_strategy(self):
        raise NotImplementedError("Should implement optimize_strategy()")
        
    @abstractmethod
    def find_best_strategy(self):
        raise NotImplementedError("Should implement best_strategy()")
        
    def print_performance(self):
        ''' Calculates and prints various Performance Metrics.
        '''
        
        data = self.results.copy()
        strategy_multiple = round(self.calculate_multiple(data.strategy), 6)
        bh_multiple =       round(self.calculate_multiple(data.returns), 6)
        outperf =           round(strategy_multiple - bh_multiple, 6)
        cagr =              round(self.calculate_cagr(data.strategy), 6)
        ann_mean =          round(self.calculate_annualized_mean(data.strategy), 6)
        ann_std =           round(self.calculate_annualized_std(data.strategy), 6)
        sharpe =            round(self.calculate_sharpe(data.strategy), 6)
       
        print(100 * "=")
        print("STRATEGY PERFORMANCE | INSTRUMENT = {} |".format(self.symbol))
        print(100 * "-")
        print("PERFORMANCE MEASURES:")
        print("\n")
        print("Multiple (Strategy):         {}".format(strategy_multiple))
        print("Multiple (Buy-and-Hold):     {}".format(bh_multiple))
        print(38 * "-")
        print("Out-/Underperformance:       {}".format(outperf))
        print("\n")
        print("CAGR:                        {}".format(cagr))
        print("Annualized Mean:             {}".format(ann_mean))
        print("Annualized Std:              {}".format(ann_std))
        print("Sharpe Ratio:                {}".format(sharpe))
        
        print(100 * "=")
        
    def calculate_multiple(self, series):
        return np.exp(series.sum())
    
    def calculate_cagr(self, series):
        return np.exp(series.sum())**(1/((series.index[-1] - series.index[0]).days / self.total_days)) - 1
    
    def calculate_annualized_mean(self, series):
        return series.mean() * self.tp_year
    
    def calculate_annualized_std(self, series):
        return series.std() * np.sqrt(self.tp_year)
    
    def calculate_sharpe(self, series):
        if series.std() == 0:
            return np.nan
        else:
            return self.calculate_cagr(series) / self.calculate_annualized_std(series)
