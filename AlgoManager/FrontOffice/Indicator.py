import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from hurst import compute_Hc
plt.style.use('seaborn')



class Indicator(object):
    
    def __init__(self, data):
        
        if isinstance(data, pd.Series):
            
            self.data = data.to_frame('Close')
            
        else:
            
            self.data = data
        
        
    def SMA(self, sma, volatility = False):
        
        data = self.data.copy()
        
        if volatility:
            return data.Close.rolling(window = sma).std()
            
        else:
            return data.Close.rolling(window = sma).mean()
    
    
    def EMA(self, ema, volatility = False):
        
        data = self.data.copy()
        
        if volatility:
            return data.Close.ewm(span = ema, adjust = True).mean()
        
        else:
            return data.Close.ewm(span = ema, adjust = True).mean()
    
    
    def Hurst(self, window):
        
        if not isinstance(window, int):
            raise ValueError(f'window must be an integer, found {window}')
            
        elif window < 100:
            raise ValueError(f'window must be greater or equal than 100, found {window}')
            
        data = self.data.copy()
        
        return data.Close.rolling(window=window).apply(lambda x: compute_Hc(x)[0]) 
    
    
    def APO(self, ema_s, ema_l):
        
        data = self.data.copy()
        fast_ema = self.EMA(ema = ema_s)
        slow_ema = self.EMA(ema = ema_l)
        difference = fast_ema.sub(slow_ema)
        data['APO'] = difference
        
        return data
    
    def MACD(self, ema_line_s, ema_line_l, ema_signal):
        
        data = self.data.copy()
        ema_s = self.EMA(ema = ema_line_s)
        ema_l = self.EMA(ema = ema_line_l)
        ema_m = self.EMA(ema = ema_signal)
        
        data['MACD_line'] = ema_s.sub(ema_l)
        data['MACD_signal'] = ema_m
        data['MACD_hist'] = data.MACD_line.sub(data.MACD_signal)
        
        return data
    
    def BollingerBands(self, sma, scaling_factor):
        
        data = self.data.copy()
        
        data['middleBand'] = self.SMA(sma)
        data['upperBand'] = data.middleBand + scaling_factor * self.SMA(sma = sma, volatility = True)
        data['lowerBand'] = data.middleBand - scaling_factor * self.SMA(sma = sma, volatility = True)
        
        return data
    
    def RSI(self, sma = None, ema = None):
        
        data = self.data.copy()
        
        delta = data.Close.diff()[1:]
        
        up, down = delta.clip(lower=0), delta.clip(upper=0)
        
        if sma:
            
            avgGain = up.rolling(window=sma).mean()
            avgLoss = down.rolling(window=sma).mean()
            
        elif ema:
            
            avgGain = up.ewm(span = ema, adjust = True).mean()
            avgLoss = down.ewm(span = ema, adjust = True).mean()
            
        rs = avgGain.div(avgLoss)
        rsi = 100.0 - (100.0 / (1 + rs))
        
        data['RSI'] = rsi
        
        return data
            
    