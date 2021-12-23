from AlgorithmicTradingManagement.AlgoManager.FrontOffice.Indicator import Indicator
from AlgorithmicTradingManagement.AlgoManager.FrontOffice.tradingBinance import TradingBinance

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance import ThreadedWebsocketManager



class DoubleCrossTrader(TradingBinance):
    
    
    def __init__(self, self, symbol, bar_length, units, stop_stream, position = 0, sma_s, sma_l):
        
        self.sma_s = sma_s
        self.sma_l = sma_l
        
        super().__init__(self, symbol, bar_length, units, stop_stream, position = 0)
        
        
    def define_strategy(self):
        
        data = self.data.copy()
        
        data = data[['Close']]
        
        data['SMA_S'] = Indicator(data.Close).SMA(self.sma_s)
        data['SMA_L'] = Indicator(data.Close).SMA(self.sma_l)
        
        data.dropna(inplace = True)
        
        data['position'] = 0
        
        cond1 = data.SMA_S > data.SMA_L
        cond2 = data.SMA_S < data.SMA_L
        
        data.loc[cond1, 'position'] = 1
        data.loc[cond2, 'position'] = -1
        
        
        self.on_data = data.copy()
        
        
        
if __name__ == "__main__":
    
    APIkey = 'your_API_key'
    APIsecret = 'your_secret_key'

    client = Client(api_key=APIkey, api_secret = APIsecret, tld = 'com', testnet = True)
    
    symbol = 'your_symbol'
    bar_length = 'your_length'
    sma_s = 4  # change it according to your analysis
    sma_l = 24 # change it according to your analysis
    units = units
    position = 0
    
    trader = DoubleCrossTrader(symbol = symbol, 
                               bar_length = bar_length, 
                               units = units, 
                               sma_s = sma_s,
                               sma_l = sma_l,
                               position = position)

    trader.start_trading(historical_days = 1/24)

