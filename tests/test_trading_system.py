"""
Unit tests for the trading system.
Run with: pytest tests/
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock

from ..src.trading_system.core.models import OHLCV, Signal, SignalType
from ..src.trading_system.data.providers import YahooFinanceProvider
from ..src.trading_system.strategies.strategies import SimpleMovingAverageStrategy, StrategyConfig
from ..src.trading_system.strategies.indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """Test technical indicator calculations"""

    def test_simple_moving_average(self):
        """Test SMA calculation"""
        prices = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
        sma = TechnicalIndicators.simple_moving_average(prices, 3)

        assert len(sma) == 4  # 6 - 3 + 1 = 4
        assert sma[0] == 11.0  # (10+11+12)/3
        assert sma[1] == 12.0  # (11+12+13)/3
        assert sma[2] == 13.0  # (12+13+14)/3
        assert sma[3] == 14.0  # (13+14+15)/3

    def test_exponential_moving_average(self):
        """Test EMA calculation"""
        prices = [10.0, 11.0, 12.0, 13.0, 14.0]
        ema = TechnicalIndicators.exponential_moving_average(prices, 3)

        assert len(ema) == 3  # First EMA is SMA of first 3, then 2 more
        assert ema[0] == 11.0  # SMA of first 3: (10+11+12)/3

    def test_rsi_calculation(self):
        """Test RSI calculation"""
        # Create price data that should generate RSI signals
        prices = [50.0] * 15  # Stable prices
        prices[14] = 40.0  # Drop to create down move

        rsi_values = TechnicalIndicators.relative_strength_index(prices, 14)
        assert len(rsi_values) == 1  # Only one RSI value after initial period
        assert rsi_values[0] < 50  # Should be below 50 due to price drop


class TestDataProviders:
    """Test data provider functionality"""

    @pytest.mark.asyncio
    async def test_yahoo_finance_provider(self):
        """Test Yahoo Finance data provider"""
        provider = YahooFinanceProvider()

        # Test with mock data since we don't want to hit real APIs in tests
        # In real tests, you would mock the yf.Ticker calls

        # This is a basic structure test
        assert hasattr(provider, 'get_historical_data')
        assert hasattr(provider, 'get_intraday_data')
        assert hasattr(provider, 'get_current_price')


class TestStrategies:
    """Test trading strategies"""

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing"""
        base_time = datetime(2023, 1, 1, 10, 0, 0)
        data = []

        # Create trending data
        for i in range(50):
            timestamp = base_time + timedelta(minutes=i*5)
            close_price = 100.0 + i * 0.5  # Trending up
            data.append(OHLCV(
                timestamp=timestamp,
                open=Decimal(str(close_price - 0.1)),
                high=Decimal(str(close_price + 0.2)),
                low=Decimal(str(close_price - 0.3)),
                close=Decimal(str(close_price)),
                volume=1000 + i * 10
            ))

        return data

    @pytest.mark.asyncio
    async def test_sma_strategy_initialization(self, sample_ohlcv_data):
        """Test SMA strategy initialization"""
        # Mock data provider
        mock_provider = Mock()
        mock_provider.get_historical_data = AsyncMock(return_value=sample_ohlcv_data)

        config = StrategyConfig(
            name="sma_crossover",
            symbol="TEST",
            parameters={"short_period": 5, "long_period": 20}
        )

        strategy = SimpleMovingAverageStrategy(config, mock_provider)

        # Initialize strategy
        await strategy.initialize()

        # Check that indicators were calculated
        assert strategy.indicator_calculator is not None

    @pytest.mark.asyncio
    async def test_signal_generation(self, sample_ohlcv_data):
        """Test signal generation"""
        # Mock data provider
        mock_provider = Mock()
        mock_provider.get_historical_data = AsyncMock(return_value=sample_ohlcv_data)

        config = StrategyConfig(
            name="sma_crossover",
            symbol="TEST",
            parameters={"short_period": 5, "long_period": 20}
        )

        strategy = SimpleMovingAverageStrategy(config, mock_provider)
        await strategy.initialize()

        # Generate signals
        signals = await strategy.generate_signals(sample_ohlcv_data)

        # Should generate some signals
        assert isinstance(signals, list)
        for signal in signals:
            assert isinstance(signal, Signal)
            assert signal.symbol == "TEST"
            assert signal.signal_type in [SignalType.BUY, SignalType.SELL, SignalType.NO_SIGNAL]


class TestModels:
    """Test data models"""

    def test_ohlcv_creation(self):
        """Test OHLCV data creation"""
        timestamp = datetime(2023, 1, 1, 10, 0, 0)
        ohlcv = OHLCV(
            timestamp=timestamp,
            open=Decimal('100.0'),
            high=Decimal('101.0'),
            low=Decimal('99.0'),
            close=Decimal('100.5'),
            volume=1000
        )

        assert ohlcv.timestamp == timestamp
        assert ohlcv.close == Decimal('100.5')
        assert ohlcv.volume == 1000

    def test_signal_creation(self):
        """Test Signal creation"""
        timestamp = datetime(2023, 1, 1, 10, 0, 0)
        signal = Signal(
            symbol="AAPL",
            signal_type=SignalType.BUY,
            timestamp=timestamp,
            price=Decimal('150.0'),
            confidence=0.8
        )

        assert signal.symbol == "AAPL"
        assert signal.signal_type == SignalType.BUY
        assert signal.confidence == 0.8


if __name__ == "__main__":
    pytest.main([__file__])