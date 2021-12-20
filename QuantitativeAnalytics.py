import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
plt.style.use('seaborn')

class FinancialAnalysis(): #Parent Class
    
    def __init__(self, ticker, start, end, interval = None, filepath = None):
        
        self._ticker = ticker
        self.start = start
        self.end = end
        self.interval = interval
        self.filepath = filepath
        self.get_data()
        self.log_returns()
        
    def __repr__(self):
        return 'FinancialAnalysis(symbol = {}, start = {}, end = {}, interval = {}, filepath = {}'.format(self._ticker, self.start, self.end, self.interval, self.filepath)
        
    def get_data(self):
        
        if self.filepath:
            
            raw = pd.read_csv(self.filepath, parse_dates = ["Date"], index_col = "Date")
            self.data = raw[self.start : self.end].Close
        
        elif self.interval:
            
            columns = ['Close','Volume']
            self.data = yf.Ticker(self._ticker).history(start = self.start, 
                                                        end = self.end, 
                                                        interval = str(self.interval))[columns]
            
    
    def plot_prices(self):
        
        plt.figure(figsize=(16,8))
        
        plt.plot(self.data.Close)
        plt.ylabel('Price')
        plt.xlabel('Date')
        plt.tick_params(axis = 'both', which = 'major', labelsize=15)
        plt.title('Price Chart : {}'.format(self._ticker))
        plt.suptitle("")
        
        plt.show()
    
    def log_returns(self):
        self.data['log_returns'] = np.log(self.data.Close/self.data.Close.shift(1))
        
    def plot_returns(self, hist):
        
        plt.figure(figsize=(16,8))
        
        if hist:
            
            plt.hist(self.data.log_returns, bins=100)
            
            plt.ylabel('Frequency Returns')
            plt.xlabel('Date')
            plt.tick_params(axis = 'both', which = 'major', labelsize=15)
            plt.title('Frequency of Returns : {}'.format(self._ticker))
            plt.suptitle("")

            plt.show()

        else:
            
            plt.plot(self.data.log_returns)
            
            plt.ylabel('log Returns')
            plt.xlabel('Date')
            plt.tick_params(axis = 'both', which = 'major', labelsize=15)
            plt.title('logReturns Chart : {}'.format(self._ticker))
            plt.suptitle("")

            plt.show()

    
    def set_ticker(self, ticker = None):
        if ticker is not None:
            self._ticker = ticker
            self.get_data()
            self.log_returns()
            
######################################################################################           
            
class RiskReturn(FinancialAnalysis): #Child Class
    
    def __init__(self, ticker, start, end, interval, freq = None):
        self.freq = freq
        super().__init__(ticker, start, end, interval) #overwrites from the Parent Class
    
    def __repr__(self):
        return 'RiskReturn(symbol = {}, start = {}, end = {}, interval = {}, filepath = {}'.format(self._ticker, self.start, self.end, self.interval, self.filepath)
    
    
    def mean_returns(self):
        
        if self.freq is None:
            return self.data.log_returns.mean()
        
        else:
            resampled_price = self.data.Close.resample(self.freq).last()
            resampled_returns = np.log(resampled_price/resampled_price.shift(1))
            return resampled_returns.mean()
        
    
    def std_returns(self):
        
        if self.freq is None:
            return self.data.log_returns.std()
        
        else:
            resampled_price = self.data.Close.resample(self.freq).last()
            resampled_returns = np.log(resampled_price/resampled_price.shift(1))
            return resampled_returns.std()
        
    def annualized_return(self, instrumentType='stock'):
        
        if (instrumentType == 'crypto') or (instrumentType == 'energyCommodity'):
            mean_return = round(self.data.log_returns.mean()*365.25,3)
            return mean_return
        
        else:
            mean_return = round(self.data.log_returns.mean()*252,3)
            return mean_return
        
    def annualized_std(self, instrumentType = 'stock'):
        
        if (instrumentType == 'crypto') or (instrumentType == 'energyCommodity'):
            risk = round(self.data.log_returns.std()*np.sqrt(252),3)
            return risk
        
        else:
            risk = round(self.data.log_returns.std()*np.sqrt(252),3)
            return risk
        
        
    def sharpe_ratio(self, instrumentType = 'stock'):
        return self.annualized_return()/self.annualized_std()
    
    def drawdown(self):
        
        multiple = self.data.log_returns.cumsum().apply(np.exp).dropna()
        previous_peaks = multiple.cummax()
        drawdowns = (multiple - previous_peaks)/previous_peaks
        return pd.DataFrame({'Wealth': multiple,
                             'Previous Peak': previous_peaks,
                             'Drawdown': drawdowns})
    
    def var_historic(self, level=5):
        '''Computes the historic Value at Risk at a specified level, i.e.
           returns the number such that the "level" percent of the returns fall
           below that number, and the (100-level) percent are above'''
        return -np.percentile(self.data.log_returns.dropna(), level)
    
    def cvar_historic(self, level=5):
        '''Computes the Conditional VaR of the returns'''
        is_beyond = self.data.log_returns.dropna() <= -self.var_historic()
        return self.data.log_returns.dropna()[is_beyond == True].mean()
    
    def performance_summary(self, instrumentType = 'stock'):
        
        ann_rets = self.annualized_return(instrumentType=instrumentType)
        ann_vol = self.annualized_std(instrumentType=instrumentType)
        ann_sr = self.sharpe_ratio(instrumentType = instrumentType)
        dd = self.drawdown().Drawdown.min()
        var = self.var_historic()
        cvar = self.cvar_historic()
        
        print(100 * "=")
        print("PERFORMANCE SUMMARY | INSTRUMENT = {} |".format(self._ticker))
        print(100 * "-")
        print("PERFORMANCE MEASURES:")
        print("\n")
        print("Annualized Returns:         {}".format(ann_rets))
        print("Annualized Volatility:     {}".format(ann_vol))
        print("Annualized Sharpe Ratio:    {}".format(ann_sr))
        print("Maximum Drawdown:           {}".format(dd))
        print(38 * "-")
        print("\n")
        print("Value at Risk:       {}".format(var))
        print("Conditional Value ar Risk      {}".format(cvar))
        print(100 * "=")
        
        
#######################################################################################




        
        
    
        
        
        