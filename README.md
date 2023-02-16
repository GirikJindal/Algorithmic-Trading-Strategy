# AlgoBulls-Assignment
A simple Algorithmic Trading Strategy

1) ``` class ScriptData ```
This code includes the ScriptData class which has methods for fetching intraday stock data from Alpha Vantage and converting it to a Pandas DataFrame. It also includes overloaded methods for getting, setting and checking for the existence of items in the class instance.

To use the class, you will need to create an instance of the class by passing in your Alpha Vantage API key.
```api_key = "<Enter API-Key here>"```

``` fetch_intraday_data(script) ```
The intraday data can be fetched for a specific stock by calling fetch_intraday_data(). The stock symbol has to be passed as argument to this method.
The fetched intraday data will be stored in the 'data' attribute of the class instance.

``` convert_intraday_data(script) ```
You can then convert the fetched data to a Pandas DataFrame by calling convert_intraday_data().
This will return a Pandas DataFrame with columns for timestamp, open price, high price, low price, closing price and volume.

There are 3 overloaded methods: __getitem__ , __setitem__ and __contains__:
``` __getitem__(key) ```: To access items in the data attribute
``` __setitem__(key, value) ``` To store items in the data attribute
``` __contains__(key) ``` To check for items in the data attribute

2) ``` indicator1(df, timeperiod) ```
The indicator() takes in a pandas DataFrame df and an integer timeperiod as arguments. It then calculates the moving average of the close column of the DataFrame with a window of size timeperiod. It creates a new DataFrame with two columns - timestamp and indicator. The timestamp column is the same as the timestamp column in the input DataFrame, while the indicator column contains the calculated moving average values.

3) ``` class Strategy ```
This class takes in a script parameter in its constructor. The fetch_signals() is defined to fetch intraday historical data for the given script using the ScriptData class, compute indicator data on the close column of the resulting DataFrame using the indicator1 function, and generates a signals DataFrame with timestamp, close_data, indicator_data, and signal columns. The signal column is determined by comparing the indicator_data and close_data columns - if the indicator_data is greater than the close_data, the signal is set to 'BUY'; if the indicator_data is less than the close_data, the signal is set to 'SELL'; otherwise, the signal is set to 'NO_SIGNAL'.

Finally, the signals DataFrame is printed, with only rows where the signal is either 'BUY' or 'SELL'.

This is set to None to avoid unnecessary warnings (SettingWithCopyWarning)
```pd.options.mode.chained_assignment = None```
