"""
Technical indicators for trading strategies.
Comprehensive collection of technical analysis indicators.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from ..core.models import OHLCV, IndicatorData
from ..core.logging import get_logger

log = get_logger(__name__)

class IndicatorType(Enum):
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    SUPPORT_RESISTANCE = "support_resistance"

@dataclass
class IndicatorResult:
    """Result of an indicator calculation"""
    name: str
    values: List[float]
    timestamps: List[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)

class TechnicalIndicators:
    """Collection of technical analysis indicators"""

    @staticmethod
    def simple_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []

        sma = []
        for i in range(len(prices) - period + 1):
            sma.append(sum(prices[i:i+period]) / period)
        return sma

    @staticmethod
    def exponential_moving_average(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []

        ema = []
        multiplier = 2 / (period + 1)

        # First EMA is SMA
        sma = sum(prices[:period]) / period
        ema.append(sma)

        # Calculate subsequent EMAs
        for price in prices[period:]:
            ema_val = (price * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_val)

        return ema

    @staticmethod
    def relative_strength_index(prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return []

        rsi_values = []
        gains = []
        losses = []

        # Calculate price changes
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))

        # Calculate initial averages
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        if avg_loss == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(100 - (100 / (1 + rs)))

        # Calculate subsequent RSI values
        for i in range(period, len(gains)):
            gain = gains[i]
            loss = losses[i]

            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return rsi_values

    @staticmethod
    def macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow_period:
            return {"macd": [], "signal": [], "histogram": []}

        fast_ema = TechnicalIndicators.exponential_moving_average(prices, fast_period)
        slow_ema = TechnicalIndicators.exponential_moving_average(prices, slow_period)

        # MACD line
        macd_line = []
        start_idx = slow_period - fast_period
        for i in range(len(slow_ema)):
            macd_line.append(fast_ema[i + start_idx] - slow_ema[i])

        # Signal line (EMA of MACD)
        signal_line = TechnicalIndicators.exponential_moving_average(macd_line, signal_period)

        # Histogram
        histogram = []
        signal_start_idx = signal_period - 1
        for i in range(len(signal_line)):
            histogram.append(macd_line[i + signal_start_idx] - signal_line[i])

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    @staticmethod
    def bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {"upper": [], "middle": [], "lower": []}

        bands = []
        for i in range(len(prices) - period + 1):
            window = prices[i:i+period]
            sma = sum(window) / period
            std = np.std(window)

            upper = sma + (std_dev * std)
            lower = sma - (std_dev * std)

            bands.append({
                "upper": upper,
                "middle": sma,
                "lower": lower
            })

        return {
            "upper": [b["upper"] for b in bands],
            "middle": [b["middle"] for b in bands],
            "lower": [b["lower"] for b in bands]
        }

    @staticmethod
    def stochastic_oscillator(
        high_prices: List[float],
        low_prices: List[float],
        close_prices: List[float],
        k_period: int = 14,
        d_period: int = 3
    ) -> Dict[str, List[float]]:
        """Calculate Stochastic Oscillator"""
        if len(close_prices) < k_period:
            return {"k": [], "d": []}

        k_values = []
        for i in range(len(close_prices) - k_period + 1):
            high_window = high_prices[i:i+k_period]
            low_window = low_prices[i:i+k_period]

            highest_high = max(high_window)
            lowest_low = min(low_window)
            current_close = close_prices[i+k_period-1]

            if highest_high - lowest_low == 0:
                k = 50.0
            else:
                k = 100 * ((current_close - lowest_low) / (highest_high - lowest_low))

            k_values.append(k)

        # %D is SMA of %K
        d_values = TechnicalIndicators.simple_moving_average(k_values, d_period)

        return {"k": k_values, "d": d_values}

    @staticmethod
    def average_true_range(
        high_prices: List[float],
        low_prices: List[float],
        close_prices: List[float],
        period: int = 14
    ) -> List[float]:
        """Calculate Average True Range (ATR)"""
        if len(close_prices) < period + 1:
            return []

        true_ranges = []
        for i in range(1, len(close_prices)):
            tr1 = high_prices[i] - low_prices[i]
            tr2 = abs(high_prices[i] - close_prices[i-1])
            tr3 = abs(low_prices[i] - close_prices[i-1])
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)

        # Calculate ATR as EMA of True Range
        return TechnicalIndicators.exponential_moving_average(true_ranges, period)

    @staticmethod
    def on_balance_volume(close_prices: List[float], volumes: List[int]) -> List[float]:
        """Calculate On Balance Volume (OBV)"""
        if len(close_prices) != len(volumes):
            raise ValueError("Close prices and volumes must have same length")

        obv = [0]
        for i in range(1, len(close_prices)):
            if close_prices[i] > close_prices[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif close_prices[i] < close_prices[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])

        return obv

class IndicatorCalculator:
    """Calculator for technical indicators from OHLCV data"""

    def __init__(self, ohlcv_data: List[OHLCV]):
        self.ohlcv_data = sorted(ohlcv_data, key=lambda x: x.timestamp)
        self.close_prices = [float(ohlcv.close) for ohlcv in self.ohlcv_data]
        self.high_prices = [float(ohlcv.high) for ohlcv in self.ohlcv_data]
        self.low_prices = [float(ohlcv.low) for ohlcv in self.ohlcv_data]
        self.volumes = [ohlcv.volume for ohlcv in self.ohlcv_data]
        self.timestamps = [ohlcv.timestamp for ohlcv in self.ohlcv_data]

    def calculate_sma(self, period: int) -> IndicatorData:
        """Calculate Simple Moving Average"""
        values = TechnicalIndicators.simple_moving_average(self.close_prices, period)
        start_idx = period - 1

        return IndicatorData(
            name="SMA",
            symbol="",  # Would be set by caller
            timestamp=self.timestamps[-1],
            value={"sma": values[-1] if values else None},
            metadata={
                "period": period,
                "values": values,
                "timestamps": self.timestamps[start_idx:]
            }
        )

    def calculate_rsi(self, period: int = 14) -> IndicatorData:
        """Calculate RSI"""
        values = TechnicalIndicators.relative_strength_index(self.close_prices, period)
        start_idx = period

        return IndicatorData(
            name="RSI",
            symbol="",
            timestamp=self.timestamps[-1],
            value={"rsi": values[-1] if values else None},
            metadata={
                "period": period,
                "values": values,
                "timestamps": self.timestamps[start_idx:]
            }
        )

    def calculate_macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> IndicatorData:
        """Calculate MACD"""
        macd_data = TechnicalIndicators.macd(
            self.close_prices, fast_period, slow_period, signal_period
        )

        return IndicatorData(
            name="MACD",
            symbol="",
            timestamp=self.timestamps[-1],
            value={
                "macd": macd_data["macd"][-1] if macd_data["macd"] else None,
                "signal": macd_data["signal"][-1] if macd_data["signal"] else None,
                "histogram": macd_data["histogram"][-1] if macd_data["histogram"] else None
            },
            metadata={
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period,
                "macd_line": macd_data["macd"],
                "signal_line": macd_data["signal"],
                "histogram": macd_data["histogram"]
            }
        )

    def calculate_bollinger_bands(
        self,
        period: int = 20,
        std_dev: float = 2.0
    ) -> IndicatorData:
        """Calculate Bollinger Bands"""
        bb_data = TechnicalIndicators.bollinger_bands(self.close_prices, period, std_dev)

        return IndicatorData(
            name="BollingerBands",
            symbol="",
            timestamp=self.timestamps[-1],
            value={
                "upper": bb_data["upper"][-1] if bb_data["upper"] else None,
                "middle": bb_data["middle"][-1] if bb_data["middle"] else None,
                "lower": bb_data["lower"][-1] if bb_data["lower"] else None
            },
            metadata={
                "period": period,
                "std_dev": std_dev,
                "upper_band": bb_data["upper"],
                "middle_band": bb_data["middle"],
                "lower_band": bb_data["lower"]
            }
        )

    def calculate_stochastic(
        self,
        k_period: int = 14,
        d_period: int = 3
    ) -> IndicatorData:
        """Calculate Stochastic Oscillator"""
        stoch_data = TechnicalIndicators.stochastic_oscillator(
            self.high_prices, self.low_prices, self.close_prices, k_period, d_period
        )

        return IndicatorData(
            name="Stochastic",
            symbol="",
            timestamp=self.timestamps[-1],
            value={
                "k": stoch_data["k"][-1] if stoch_data["k"] else None,
                "d": stoch_data["d"][-1] if stoch_data["d"] else None
            },
            metadata={
                "k_period": k_period,
                "d_period": d_period,
                "k_values": stoch_data["k"],
                "d_values": stoch_data["d"]
            }
        )