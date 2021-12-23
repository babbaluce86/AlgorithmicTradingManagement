from AlgorithmicTradingManagement.AlgoManager.FrontOffice.Indicator import Indicator
from AlgorithmicTradingManagement.AlgoManager.FrontOffice.tradingBinance import TradingBinance

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance import ThreadedWebsocketManager


class APOTrader(TradingBinance):
    
    
    def __init__(self, self, symbol, bar_length, units, stop_stream, position = 0, ema_s, ema_l):
        
        self.ema_s = ema_s
        self.ema_l = ema_l
        
        super().__init__(self, symbol, bar_length, units, stop_stream, position = 0)
        
        
    def define_strategy(self):
        
        data = self.data.copy()
        
        data = data[['Close']]
        
        data = Indicator(data).APO(self.ema_s, self.ema_l)
        
        data.dropna(inplace = True)
        
        data['position'] = 0
        
        cond1 = data.APO > 0
        cond2 = data.APO < 0
        
        data.loc[cond1, 'position'] = 1
        data.loc[cond2, 'position'] = -1
        
        self.on_data = data.copy()
        
        
        
if __name__ == "__main__":
    
    APIkey = 'your_API_key'
    APIsecret = 'your_secret_key'

    client = Client(api_key=APIkey, api_secret = APIsecret, tld = 'com', testnet = True)
    
    symbol = 'your_symbol'
    barl_length = 'your_length'
    
    ema_s = 9 # change it according to your analysis
    ema_l = 14 # change it according to your analysis
    
    units = units
    position = 0
    
    trader = APOTrader(symbol = symbol, 
                       bar_length = bar_length, 
                       ema_s = ema_s
                       ema_l = ema_l
                       units = units, 
                       position = position)

    trader.start_trading(historical_days = 1/24)

