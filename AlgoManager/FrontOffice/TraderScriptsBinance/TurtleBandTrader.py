from AlgorithmicTradingManagement.AlgoManager.FrontOffice.Indicator import Indicator
from AlgorithmicTradingManagement.AlgoManager.FrontOffice.tradingBinance import TradingBinance

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from binance.client import Client
from binance import ThreadedWebsocketManager


class TurtleBandTrader(TradingBinance):
    
    
    def __init__(self, self, symbol, bar_length, units, stop_stream, position = 0, sma, scaling_factor):
        
        self.sma = sma
        self.scaling_factor = scaling_factor 
        
        self.your_multiple_strategy_parameters = your_strategy_parameters
        super().__init__(self, symbol, bar_length, units, stop_stream, position = 0)
        
        
    def define_strategy(self):
        
        data = self.data.copy()
        
        window = self.sma
        scaled = self.scaling_factor
        
        data = self.data[['Close']].copy()
        
        data = Indicator(data).BollingerBands(sma = window, 
                                             scaling_factor = scaled)
        
        data['distance'] = data.Close - data.middleBand
        
        data.dropna(inplace = True)
        
        data['positions'] = 0
        
        cond1 = data.Close > data.upperBand 
        cond2 = data.Close < data.lowerBand 
        cond3 = data.distance * data.distance.shift(1) < 0
        
        data.loc[cond1, 'positions'] = 1
        data.loc[cond2, 'positions'] = -1
        data.loc[cond3, 'positions'] = 0
        
        self.on_data = data.copy()
        
        
        
if __name__ == "__main__":
    
    APIkey = 'your_API_key'
    APIsecret = 'your_secret_key'

    client = Client(api_key=APIkey, api_secret = APIsecret, tld = 'com', testnet = True)
    
    symbol = 'your_symbol'
    bar_length = 'your_length'
    sma = 48 # change it according to your analysis
    scaling_factor = 2.5 # change it according to your analysis
    units = units
    position = 0
    
    trader = TurtleBandTrader(symbol = symbol, 
                              bar_length = bar_length, 
                              units = units, 
                              sma = sma,
                              scaling_factor = scaling_factor,
                              position = position)

    trader.start_trading(historical_days = 1/24)

