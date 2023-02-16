# AlgoBulls-Assignment
A simple Algorithmic Trading Strategy

This code includes the ScriptData class which has methods for fetching intraday stock data from Alpha Vantage and converting it to a Pandas DataFrame. It also includes overloaded methods for getting, setting and checking for the existence of items in the class instance.

To use the class, you will need to create an instance of the class by passing in your Alpha Vantage API key.

The intraday data can be fetched for a specific stock by calling fetch_intraday_data(). The stock symbol has to be passed as argument to this method.
The fetched intraday data will be stored in the 'data' attribute of the class instance.

You can then convert the fetched data to a Pandas DataFrame by calling convert_intraday_data().
This will return a Pandas DataFrame with columns for timestamp, open price, high price, low price, closing price and volume.

Finally, you can access items in the data attribute of the class instance using __getitem__().

