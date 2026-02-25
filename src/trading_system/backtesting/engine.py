"""
Backtesting framework for trading strategies.
Comprehensive backtesting with performance metrics and risk analysis.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import statistics

from ..core.models import (
    OHLCV, Trade, Portfolio, BacktestResult,
    Order, OrderSide, OrderType, Signal, SignalType
)
from ..data.providers import DataProvider
from ..strategies.strategies import TradingStrategy, StrategyConfig
from ..core.logging import get_logger

log = get_logger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    start_date: datetime
    end_date: datetime
    initial_capital: Decimal = Decimal('100000')
    commission_per_trade: Decimal = Decimal('0.001')  # 0.1%
    slippage: Decimal = Decimal('0.0005')  # 0.05%
    max_position_size: float = 0.1  # Max 10% of portfolio per position

@dataclass
class BacktestPosition:
    """Position during backtesting"""
    symbol: str
    quantity: Decimal
    entry_price: Decimal
    entry_date: datetime
    current_price: Decimal = Decimal('0')
    market_value: Decimal = Decimal('0')
    unrealized_pnl: Decimal = Decimal('0')

class BacktestEngine:
    """Engine for running trading strategy backtests"""

    def __init__(self, config: BacktestConfig, data_provider: DataProvider):
        self.config = config
        self.data_provider = data_provider
        self.portfolio = Portfolio(
            total_value=config.initial_capital,
            cash=config.initial_capital
        )
        self.positions: Dict[str, BacktestPosition] = {}
        self.trades: List[Trade] = []
        self.portfolio_history: List[Dict[str, Any]] = []

    async def run_backtest(
        self,
        strategy: TradingStrategy
    ) -> BacktestResult:
        """Run backtest for the given strategy"""

        log.info(f"Starting backtest for {strategy.config.name} from {self.config.start_date} to {self.config.end_date}")

        # Get historical data
        historical_data = await self.data_provider.get_historical_data(
            strategy.config.symbol,
            self.config.start_date,
            self.config.end_date
        )

        if not historical_data:
            raise ValueError("No historical data available for backtest")

        # Initialize strategy
        await strategy.initialize()

        # Process each data point
        for i, ohlcv in enumerate(historical_data):
            current_data = historical_data[:i+1]

            # Update portfolio values
            await self._update_portfolio_values(current_data[-1])

            # Generate signals
            signals = await strategy.generate_signals(current_data)

            # Execute signals
            for signal in signals:
                await self._execute_signal(signal, ohlcv.timestamp)

            # Record portfolio state
            self._record_portfolio_state(ohlcv.timestamp)

        # Calculate final results
        result = self._calculate_results(strategy.config.name, strategy.config.symbol)

        log.info(f"Backtest completed. Final portfolio value: ${result.final_capital}")
        return result

    async def _update_portfolio_values(self, current_ohlcv: OHLCV):
        """Update portfolio values with current prices"""
        total_value = self.portfolio.cash

        for symbol, position in self.positions.items():
            # Update position with current price (assuming single symbol for now)
            position.current_price = current_ohlcv.close
            position_value = position.quantity * position.current_price
            total_value += position_value

            # Calculate unrealized P&L
            position.market_value = position_value
            position.unrealized_pnl = position_value - (position.quantity * position.entry_price)

        self.portfolio.total_value = total_value

    async def _execute_signal(self, signal: Signal, timestamp: datetime):
        """Execute a trading signal"""
        if signal.signal_type not in [SignalType.BUY, SignalType.SELL]:
            return

        # Calculate position size
        position_value = self.portfolio.total_value * Decimal(str(self.config.max_position_size))
        quantity = (position_value / signal.price).quantize(Decimal('1'), rounding=ROUND_DOWN)

        if quantity <= 0:
            return

        # Apply slippage and commission
        slippage_decimal = Decimal(str(self.config.slippage))
        execution_price = signal.price * (Decimal('1') + slippage_decimal)
        if signal.signal_type == SignalType.SELL:
            execution_price = signal.price * (Decimal('1') - slippage_decimal)

        commission = execution_price * quantity * self.config.commission_per_trade

        if signal.signal_type == SignalType.BUY:
            # Buy signal
            cost = (execution_price * quantity) + commission

            if cost > self.portfolio.cash:
                log.warning(f"Insufficient cash for buy order: {cost} > {self.portfolio.cash}")
                return

            # Create or update position
            if signal.symbol in self.positions:
                position = self.positions[signal.symbol]
                total_quantity = position.quantity + quantity
                total_cost = (position.quantity * position.entry_price) + (quantity * execution_price)
                position.entry_price = total_cost / total_quantity
                position.quantity = total_quantity
            else:
                self.positions[signal.symbol] = BacktestPosition(
                    symbol=signal.symbol,
                    quantity=quantity,
                    entry_price=execution_price,
                    entry_date=timestamp,
                    current_price=execution_price
                )

            self.portfolio.cash -= cost

            # Record trade
            trade = Trade(
                symbol=signal.symbol,
                side=OrderSide.BUY,
                quantity=quantity,
                price=execution_price,
                timestamp=timestamp,
                commission=commission
            )
            self.trades.append(trade)

        else:  # Sell signal
            if signal.symbol not in self.positions:
                return

            position = self.positions[signal.symbol]
            sell_quantity = min(quantity, position.quantity)

            proceeds = (execution_price * sell_quantity) - commission
            self.portfolio.cash += proceeds

            # Calculate realized P&L
            cost_basis = sell_quantity * position.entry_price
            realized_pnl = proceeds - cost_basis - commission
            position.realized_pnl += realized_pnl

            # Update position
            position.quantity -= sell_quantity
            if position.quantity <= 0:
                del self.positions[signal.symbol]

            # Record trade
            trade = Trade(
                symbol=signal.symbol,
                side=OrderSide.SELL,
                quantity=sell_quantity,
                price=execution_price,
                timestamp=timestamp,
                commission=commission,
                pnl=realized_pnl
            )
            self.trades.append(trade)

    def _record_portfolio_state(self, timestamp: datetime):
        """Record current portfolio state"""
        state = {
            "timestamp": timestamp,
            "total_value": float(self.portfolio.total_value),
            "cash": float(self.portfolio.cash),
            "positions": {
                symbol: {
                    "quantity": float(pos.quantity),
                    "market_value": float(pos.market_value),
                    "unrealized_pnl": float(pos.unrealized_pnl)
                }
                for symbol, pos in self.positions.items()
            }
        }
        self.portfolio_history.append(state)

    def _calculate_results(self, strategy_name: str, symbol: str) -> BacktestResult:
        """Calculate backtest results and performance metrics"""

        if not self.portfolio_history:
            return BacktestResult(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=self.config.start_date,
                end_date=self.config.end_date,
                initial_capital=float(self.config.initial_capital),
                final_capital=float(self.config.initial_capital),
                total_return=0.0,
                annualized_return=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0
            )

        # Basic metrics
        initial_capital = float(self.config.initial_capital)
        final_capital = float(self.portfolio.total_value)
        total_return = (final_capital - initial_capital) / initial_capital

        # Calculate daily returns for advanced metrics
        daily_returns = []
        prev_value = initial_capital

        for state in self.portfolio_history:
            current_value = state["total_value"]
            daily_return = (current_value - prev_value) / prev_value
            daily_returns.append(daily_return)
            prev_value = current_value

        # Annualized return
        days = (self.config.end_date - self.config.start_date).days
        if days > 0:
            annualized_return = (1 + total_return) ** (365 / days) - 1
        else:
            annualized_return = 0.0

        # Maximum drawdown
        max_drawdown = 0.0
        peak = initial_capital

        for state in self.portfolio_history:
            current_value = state["total_value"]
            if current_value > peak:
                peak = current_value
            drawdown = (peak - current_value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # Sharpe ratio (assuming 0% risk-free rate)
        if len(daily_returns) > 1 and statistics.stdev(daily_returns) > 0:
            sharpe_ratio = statistics.mean(daily_returns) / statistics.stdev(daily_returns) * (252 ** 0.5)  # Annualized
        else:
            sharpe_ratio = 0.0

        return BacktestResult(
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trades=self.trades,
            portfolio_values=self.portfolio_history
        )

class BacktestRunner:
    """High-level backtest runner"""

    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    async def run_strategy_backtest(
        self,
        strategy_name: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0,
        strategy_params: Optional[Dict[str, Any]] = None
    ) -> BacktestResult:
        """Run a backtest for a specific strategy"""

        # Create strategy config
        config = StrategyConfig(
            name=strategy_name,
            symbol=symbol,
            parameters=strategy_params or {}
        )

        # Create strategy
        from ..strategies.strategies import StrategyFactory
        strategy = StrategyFactory.create_strategy(strategy_name, config, self.data_provider)

        # Create backtest config
        backtest_config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=Decimal(str(initial_capital))
        )

        # Run backtest
        engine = BacktestEngine(backtest_config, self.data_provider)
        result = await engine.run_backtest(strategy)

        return result

    async def compare_strategies(
        self,
        strategies: List[str],
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0
    ) -> Dict[str, BacktestResult]:
        """Compare multiple strategies"""

        results = {}
        for strategy_name in strategies:
            try:
                result = await self.run_strategy_backtest(
                    strategy_name, symbol, start_date, end_date, initial_capital
                )
                results[strategy_name] = result
                log.info(f"Completed backtest for {strategy_name}: {result.total_return:.2%} return")
            except Exception as e:
                log.error(f"Failed to run backtest for {strategy_name}: {e}")
                print(f"DEBUG: Exception for {strategy_name}: {e}")  # Debug print

        return results