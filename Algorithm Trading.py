import pandas as pd
import requests
from datetime import datetime
from sys import exit as sys_exit

pd.options.mode.chained_assignment = None   #To prevent warnings

class ScriptData:
    '''
    This class has methods for fetching intraday stock data from Alpha Vantage and converting it to a Pandas DataFrame. 
    It also includes overloaded methods for getting, setting and checking for the existence of items in the class instance.
    To use the class, you will need to create an instance of the class by passing in your Alpha Vantage API key.
    '''
    def __init__(self, api_key):
        self.api_key = api_key     #API Key

    def fetch_intraday_data(self, script):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={script}&interval=5min&apikey={self.api_key}' 
        response = requests.get(url)    #Load data from URL
        self.data = response.json()

    def convert_intraday_data(self, script):
        try:
            data = self.data[f'Time Series (5min)']
        except:
            print('Error')  #Error raised if an invalid script has been requested
            sys_exit()
        rows = []
        for key, value in data.items():
            row = {'timestamp': datetime.strptime(key, '%Y-%m-%d %H:%M:%S'),
                   'open': float(value['1. open']),
                   'high': float(value['2. high']),
                   'low': float(value['3. low']),
                   'close': float(value['4. close']),
                   'volume': int(value['5. volume'])}
            rows.append(row)
        df = pd.DataFrame(rows)
        return df

    def __getitem__(self, key):
        return self.data[key]   #get

    def __setitem__(self, key, value):
        self.data[key] = value  #store

    def __contains__(self, key):
        return key in self.data #check

api_key = "125LHM3ZMNTITEIE"    #api-key
script_data = ScriptData(api_key)

#script = input()

#script_data.fetch_intraday_data(script)
#df = script_data.convert_intraday_data(script)
#print(df)

def indicator1(df, timeperiod):
    ma = df['close'].rolling(window=timeperiod).mean() #moving average
    return pd.DataFrame({'timestamp': df['timestamp'], 'indicator': ma})

#ma_df = indicator1(df, 5)
#print(ma_df)

class Strategy:
    '''
    Generate a pandas DataFrame called ‘signals’ with 2 columns:
        i. ‘timestamp’: Same as ‘timestamp’ column in ‘df’
        ii. ‘signal’: This column can have values: BUY, SELL and NO_SIGNAL
    '''
    def __init__(self, script):
        self.script = script

    def get_script_data(self):
        # Fetch intraday historical data for script
        self.data = ScriptData(api_key)
        self.data.fetch_intraday_data(self.script) 
        self.df = self.data.convert_intraday_data(self.script)
        
    def get_signals(self):        
        # Compute indicator data on close column of df
        indicator_data = indicator1(self.df, 5)['indicator']
        
        # Generate signals DataFrame
        signals = pd.DataFrame({'timestamp': self.df['timestamp']})
        signals['signal'] = 'NO_SIGNAL'    #not included
        signals['signal'][indicator_data > self.df['close']] = 'BUY'  
        signals['signal'][indicator_data < self.df['close']] = 'SELL'
        
        # Print signals DataFrame with only BUY and SELL signals
        print(signals.loc[signals['signal'].isin(['BUY', 'SELL'])])

strategy = Strategy(script) 
#strategy.get_script_data()
#strategy.get_signals()

input('\nPress any key to exit...')     #Exit
