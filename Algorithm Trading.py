import pandas as pd
import requests
from datetime import datetime
from sys import exit as sys_exit

pd.options.mode.chained_assignment = None

class ScriptData:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_intraday_data(self, script):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={script}&interval=5min&apikey={self.api_key}'
        response = requests.get(url)
        self.data = response.json()

    def convert_intraday_data(self, script):
        try:
            data = self.data[f'Time Series (5min)']
        except:
            print('Error')
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
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

api_key = "125LHM3ZMNTITEIE"
script_data = ScriptData(api_key)

#script = input()

#script_data.fetch_intraday_data(script)
#df = script_data.convert_intraday_data(script)
#print(df)

def indicator1(df, timeperiod):
    ma = df['close'].rolling(window=timeperiod).mean()
    return pd.DataFrame({'timestamp': df['timestamp'], 'indicator': ma})

#ma_df = indicator1(df, 5)
#print(ma_df)

class Strategy:
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
        signals['signal'] = 'NO_SIGNAL'
        signals['signal'][indicator_data > self.df['close']] = 'BUY'
        signals['signal'][indicator_data < self.df['close']] = 'SELL'
        
        # Print signals DataFrame with only BUY and SELL signals
        print(signals.loc[signals['signal'].isin(['BUY', 'SELL'])])

strategy = Strategy(script)
#strategy.get_script_data()
#strategy.get_signals()

input('\nPress any key to exit...')
