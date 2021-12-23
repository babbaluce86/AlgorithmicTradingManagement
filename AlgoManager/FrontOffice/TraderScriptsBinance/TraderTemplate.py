import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance import ThreadedWebsocketManager

from FrontOffice.tradingBinance import TradingBinance


class NameTrader(TradingBinance):
    
    
    def __init__(self, self, symbol, bar_length, units, stop_stream, position = 0, your_strategy_parameters):
        self.your_multiple_strategy_parameters = your_strategy_parameters
        super().__init__(self, symbol, bar_length, units, stop_stream, position = 0)
        
        
    def define_strategy(self):
        
        data = self.data.copy()
        
        data = data[['YOUR_COLUMNS']]
        
        ####### YOUR TRADING RULES ######
        
        
        self.on_data = data.copy()
        
        
        
if __name__ == "__main__":
    
    APIkey = 'your_API_key'
    APIsecret = 'your_secret_key'

    client = Client(api_key=APIkey, api_secret = APIsecret, tld = 'com', testnet = True)
    
    symbol = 'your_symbol'
    barl_length = 'your_length'
    your_strategy_parameters = your_strategy_parameters
    units = units
    position = 0
    
    trader = NameTrader(symbol = symbol, bar_length = bar_length,                         your_strategy_parameters = your_strategy_parameters
                        units = units, 
                        position = position)

    trader.start_trading(historical_days = 1/24)

