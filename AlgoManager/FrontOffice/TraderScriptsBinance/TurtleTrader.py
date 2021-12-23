import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance import ThreadedWebsocketManager

from FrontOffice.tradingBinance import TradingBinance


class TurtleTrader(TradingBinance):
    
    
    def __init__(self, self, symbol, bar_length, units, stop_stream, position = 0, sma):
        
        self.sma = sma
        
        super().__init__(self, symbol, bar_length, units, stop_stream, position = 0)
        
        
    def define_strategy(self):
        
        data = self.data.copy()
        
        data = data[['Close']]
        
        data['high'] = data.Close.rolling(window=self.sma).max()
        data['low'] = data.Close.rolling(window=self.sma).min()
        data['avg'] = data.Close.rolling(window=self.sma).mean()
        
        data.dropna(inplace = True)
        
        data['position'] = 0
        
        cond1 = (data.Close > data.high) & (data.Close > data.avg)
        cond2 = (data.Close < data.low) & (data.Close < data.avg)
        
        
        data.loc[cond1, 'position'] = -1
        data.loc[cond2, 'position'] = 1
        
        
        self.on_data = data.copy()
        
        
        
if __name__ == "__main__":
    
    APIkey = 'your_API_key'
    APIsecret = 'your_secret_key'

    client = Client(api_key=APIkey, api_secret = APIsecret, tld = 'com', testnet = True)
    
    symbol = 'your_symbol'
    bar_length = 'your_length'
    sma = 48 # change it according to your analysis
    units = units
    position = 0
    
    trader = TurtleTrader(symbol = symbol, 
                        bar_length = bar_length, 
                        sma = sma,
                        units = units, 
                        position = position)

    trader.start_trading(historical_days = 1/24)

