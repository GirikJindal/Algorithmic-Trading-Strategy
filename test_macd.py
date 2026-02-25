import sys
sys.path.insert(0, 'src')
from trading_system.strategies.indicators import TechnicalIndicators

# Test MACD with simple data
prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
print(f'Prices length: {len(prices)}')

macd_result = TechnicalIndicators.macd(prices, 12, 26, 9)
print(f'MACD line length: {len(macd_result["macd"])}')
print(f'Signal line length: {len(macd_result["signal"])}')
print(f'Histogram length: {len(macd_result["histogram"])}')

# Test EMA lengths
fast_ema = TechnicalIndicators.exponential_moving_average(prices, 12)
slow_ema = TechnicalIndicators.exponential_moving_average(prices, 26)
print(f'Fast EMA length: {len(fast_ema)}')
print(f'Slow EMA length: {len(slow_ema)}')