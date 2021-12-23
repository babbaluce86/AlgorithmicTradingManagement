from AlgorithmicTradingManagement.AlgoManager.FrontOffice.Indicator import Indicator
from AlgorithmicTradingManagement.AlgoManager.FrontOffice.tradingBinance import TradingBinance

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance import ThreadedWebsocketManager


def hurst_indicator(series, window):
    
    if window < 100:
        raise ValueError('window must be greater or equal than 100')
        
    return series.rolling(window=window).apply(lambda x: compute_Hc(x)[0])


class HurstCrossTrader(TradingBinance):
    
    
    def __init__(self, self, symbol, bar_length, units, stop_stream, position = 0, h_s, h_l):
        self.h_s = h_s
        self.h_l = h_l
        
        super().__init__(self, symbol, bar_length, units, stop_stream, position = 0)
        
        
    def define_strategy(self):
        
        data = self.data.copy()
        
        data = data[['Close']]
        
        data['H_S'] = hurst_indicator(data.Close, window = self.h_s)
        data['H_L'] = hurst_indicator(data.Close, window = self.h_l)
        
        data.dropna(inplace = True)
        
        data['position'] = 0
        
        cond = (data.H_S >= .6) & (data.H_L >=.6)
        cond1 = data.H_S > data.H_L
        cond2 = data.H_S < data.H_L
        
        data.loc[cond & cond1, 'position'] = 1
        data.loc[cond & cond2, 'position'] = -1
        
        self.on_data = data.copy()
        
        
        
if __name__ == "__main__":
    
    APIkey = 'your_API_key'
    APIsecret = 'your_secret_key'

    client = Client(api_key=APIkey, api_secret = APIsecret, tld = 'com', testnet = True)
    
    symbol = 'your_symbol'
    bar_length = 'your_length'
    units = units
    h_s = 100 # change it according to your analysis
    h_l = 300 # change it according to your analysis
    position = 0
    
    trader = HurstCrossTrader(symbol = symbol, 
                              bar_length = bar_length,  
                              units = units,
                              h_s = h_s
                              h_l = h_l
                              position = position)

    trader.start_trading(historical_days = 1/24)

