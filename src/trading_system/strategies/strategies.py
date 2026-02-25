"""
Trading strategy framework.
Base classes and implementations for trading strategies.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from ..core.models import OHLCV, Signal, SignalType, IndicatorData
from ..data.providers import DataProvider
from .indicators import IndicatorCalculator
from ..core.logging import get_logger

log = get_logger(__name__)

@dataclass
class StrategyConfig:
    """Configuration for a trading strategy"""
    name: str
    symbol: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_management: Dict[str, Any] = field(default_factory=dict)

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""

    def __init__(self, config: StrategyConfig, data_provider: DataProvider):
        self.config = config
        self.data_provider = data_provider
        self.indicator_calculator = None

    @abstractmethod
    async def initialize(self):
        """Initialize the strategy with historical data"""
        pass

    @abstractmethod
    async def generate_signals(self, current_data: List[OHLCV]) -> List[Signal]:
        """Generate trading signals based on current market data"""
        pass

    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """Return list of required technical indicators"""
        pass

    async def update_indicators(self, ohlcv_data: List[OHLCV]):
        """Update technical indicators with new data"""
        self.indicator_calculator = IndicatorCalculator(ohlcv_data)

class SimpleMovingAverageStrategy(TradingStrategy):
    """Simple Moving Average Crossover Strategy"""

    def get_required_indicators(self) -> List[str]:
        return ["SMA"]

    async def initialize(self):
        """Initialize with historical data"""
        # Get historical data for indicator calculation
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 2)  # 2 years of data

        historical_data = await self.data_provider.get_historical_data(
            self.config.symbol, start_date, end_date
        )

        await self.update_indicators(historical_data)
        log.info(f"Initialized {self.config.name} strategy for {self.config.symbol}")

    async def generate_signals(self, current_data: List[OHLCV]) -> List[Signal]:
        """Generate signals based on SMA crossover"""
        if not self.indicator_calculator:
            return []

        # Get current price
        current_price = current_data[-1].close

        # Calculate short and long SMAs
        short_period = self.config.parameters.get("short_period", 5)
        long_period = self.config.parameters.get("long_period", 20)

        short_sma_indicator = self.indicator_calculator.calculate_sma(short_period)
        long_sma_indicator = self.indicator_calculator.calculate_sma(long_period)

        short_sma_values = short_sma_indicator.metadata.get("values", [])
        long_sma_values = long_sma_indicator.metadata.get("values", [])

        if not short_sma_values or not long_sma_values:
            return []

        # Get latest values
        short_sma = short_sma_values[-1]
        long_sma = long_sma_values[-1]

        # Generate signal based on crossover
        signal_type = SignalType.NO_SIGNAL

        if len(short_sma_values) >= 2 and len(long_sma_values) >= 2:
            prev_short_sma = short_sma_values[-2]
            prev_long_sma = long_sma_values[-2]

            # Bullish crossover: short SMA crosses above long SMA
            if prev_short_sma <= prev_long_sma and short_sma > long_sma:
                signal_type = SignalType.BUY
            # Bearish crossover: short SMA crosses below long SMA
            elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
                signal_type = SignalType.SELL

        if signal_type != SignalType.NO_SIGNAL:
            signal = Signal(
                symbol=self.config.symbol,
                signal_type=signal_type,
                timestamp=current_data[-1].timestamp,
                price=current_price,
                confidence=0.7,
                metadata={
                    "short_sma": short_sma,
                    "long_sma": long_sma,
                    "strategy": "SMA Crossover"
                }
            )
            return [signal]

        return []

class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy"""

    def get_required_indicators(self) -> List[str]:
        return ["RSI"]

    async def initialize(self):
        """Initialize with historical data"""
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 1)

        historical_data = await self.data_provider.get_historical_data(
            self.config.symbol, start_date, end_date
        )

        await self.update_indicators(historical_data)
        log.info(f"Initialized RSI strategy for {self.config.symbol}")

    async def generate_signals(self, current_data: List[OHLCV]) -> List[Signal]:
        """Generate signals based on RSI levels"""
        if not self.indicator_calculator:
            return []

        current_price = current_data[-1].close

        # Get RSI parameters
        rsi_period = self.config.parameters.get("rsi_period", 14)
        oversold_level = self.config.parameters.get("oversold", 30)
        overbought_level = self.config.parameters.get("overbought", 70)

        rsi_indicator = self.indicator_calculator.calculate_rsi(rsi_period)
        rsi_values = rsi_indicator.metadata.get("values", [])

        if not rsi_values:
            return []

        current_rsi = rsi_values[-1]

        signal_type = SignalType.NO_SIGNAL

        # Generate signals based on RSI levels
        if current_rsi <= oversold_level:
            signal_type = SignalType.BUY
        elif current_rsi >= overbought_level:
            signal_type = SignalType.SELL

        if signal_type != SignalType.NO_SIGNAL:
            signal = Signal(
                symbol=self.config.symbol,
                signal_type=signal_type,
                timestamp=current_data[-1].timestamp,
                price=current_price,
                confidence=abs(50 - current_rsi) / 50,  # Higher confidence further from 50
                metadata={
                    "rsi": current_rsi,
                    "rsi_period": rsi_period,
                    "oversold": oversold_level,
                    "overbought": overbought_level,
                    "strategy": "RSI"
                }
            )
            return [signal]

        return []

class MACDStrategy(TradingStrategy):
    """MACD-based trading strategy"""

    def get_required_indicators(self) -> List[str]:
        return ["MACD"]

    async def initialize(self):
        """Initialize with historical data"""
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 1)

        historical_data = await self.data_provider.get_historical_data(
            self.config.symbol, start_date, end_date
        )

        await self.update_indicators(historical_data)
        log.info(f"Initialized MACD strategy for {self.config.symbol}")

    async def generate_signals(self, current_data: List[OHLCV]) -> List[Signal]:
        """Generate signals based on MACD crossover"""
        if not self.indicator_calculator:
            return []

        current_price = current_data[-1].close

        macd_indicator = self.indicator_calculator.calculate_macd()
        macd_line = macd_indicator.metadata.get("macd_line", [])
        signal_line = macd_indicator.metadata.get("signal_line", [])

        if not macd_line or not signal_line or len(macd_line) < 2 or len(signal_line) < 2:
            return []

        # Check for crossover
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        prev_macd = macd_line[-2]
        prev_signal = signal_line[-2]

        signal_type = SignalType.NO_SIGNAL

        # Bullish crossover: MACD crosses above signal line
        if prev_macd <= prev_signal and current_macd > current_signal:
            signal_type = SignalType.BUY
        # Bearish crossover: MACD crosses below signal line
        elif prev_macd >= prev_signal and current_macd < current_signal:
            signal_type = SignalType.SELL

        if signal_type != SignalType.NO_SIGNAL:
            signal = Signal(
                symbol=self.config.symbol,
                signal_type=signal_type,
                timestamp=current_data[-1].timestamp,
                price=current_price,
                confidence=0.8,
                metadata={
                    "macd": current_macd,
                    "signal": current_signal,
                    "histogram": macd_indicator.metadata.get("histogram", [])[-1],
                    "strategy": "MACD Crossover"
                }
            )
            return [signal]

        return []

class MultiIndicatorStrategy(TradingStrategy):
    """Strategy combining multiple indicators"""

    def get_required_indicators(self) -> List[str]:
        return ["SMA", "RSI", "MACD", "BollingerBands"]

    async def initialize(self):
        """Initialize with historical data"""
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 2)

        historical_data = await self.data_provider.get_historical_data(
            self.config.symbol, start_date, end_date
        )

        await self.update_indicators(historical_data)
        log.info(f"Initialized multi-indicator strategy for {self.config.symbol}")

    async def generate_signals(self, current_data: List[OHLCV]) -> List[Signal]:
        """Generate signals based on multiple indicators"""
        if not self.indicator_calculator:
            return []

        current_price = current_data[-1].close

        # Calculate all indicators
        sma_indicator = self.indicator_calculator.calculate_sma(20)
        rsi_indicator = self.indicator_calculator.calculate_rsi(14)
        macd_indicator = self.indicator_calculator.calculate_macd()
        bb_indicator = self.indicator_calculator.calculate_bollinger_bands()

        # Extract current values
        sma_20 = sma_indicator.value.get("sma")
        rsi = rsi_indicator.value.get("rsi")
        macd = macd_indicator.value.get("macd")
        signal_line = macd_indicator.value.get("signal")
        bb_upper = bb_indicator.value.get("upper")
        bb_lower = bb_indicator.value.get("lower")

        if not all([sma_20, rsi, macd, signal_line, bb_upper, bb_lower]):
            return []

        # Scoring system for signal strength
        buy_signals = 0
        sell_signals = 0
        total_signals = 0

        # RSI signals
        if rsi <= 30:
            buy_signals += 1
        elif rsi >= 70:
            sell_signals += 1
        total_signals += 1

        # MACD signals
        if macd > signal_line:
            buy_signals += 1
        else:
            sell_signals += 1
        total_signals += 1

        # Bollinger Band signals
        if current_price <= bb_lower:
            buy_signals += 1
        elif current_price >= bb_upper:
            sell_signals += 1
        total_signals += 1

        # SMA trend
        if current_price > sma_20:
            buy_signals += 0.5  # Half weight for trend
        else:
            sell_signals += 0.5
        total_signals += 0.5

        # Determine signal based on majority
        buy_ratio = buy_signals / total_signals
        sell_ratio = sell_signals / total_signals

        signal_type = SignalType.NO_SIGNAL
        confidence = 0.0

        if buy_ratio >= 0.6:  # 60%+ agreement for buy
            signal_type = SignalType.BUY
            confidence = buy_ratio
        elif sell_ratio >= 0.6:  # 60%+ agreement for sell
            signal_type = SignalType.SELL
            confidence = sell_ratio

        if signal_type != SignalType.NO_SIGNAL:
            signal = Signal(
                symbol=self.config.symbol,
                signal_type=signal_type,
                timestamp=current_data[-1].timestamp,
                price=current_price,
                confidence=confidence,
                metadata={
                    "rsi": rsi,
                    "macd": macd,
                    "signal_line": signal_line,
                    "sma_20": sma_20,
                    "bb_upper": bb_upper,
                    "bb_lower": bb_lower,
                    "buy_signals": buy_signals,
                    "sell_signals": sell_signals,
                    "strategy": "Multi-Indicator"
                }
            )
            return [signal]

        return []

class StrategyFactory:
    """Factory for creating trading strategies"""

    @staticmethod
    def create_strategy(
        strategy_name: str,
        config: StrategyConfig,
        data_provider: DataProvider
    ) -> TradingStrategy:
        """Create a strategy instance"""

        strategies = {
            "sma_crossover": SimpleMovingAverageStrategy,
            "rsi": RSIStrategy,
            "macd": MACDStrategy,
            "multi_indicator": MultiIndicatorStrategy
        }

        if strategy_name not in strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return strategies[strategy_name](config, data_provider)