"""
Risk management for trading strategies.
Position sizing, stop losses, and risk controls.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..core.models import Portfolio, Position, Signal
from ..core.logging import get_logger

log = get_logger(__name__)

class RiskModel(Enum):
    FIXED_PERCENTAGE = "fixed_percentage"
    KELLY_CRITERION = "kelly_criterion"
    FIXED_AMOUNT = "fixed_amount"

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_portfolio_risk: float = 0.02  # Max 2% portfolio risk per trade
    max_position_size: float = 0.1   # Max 10% of portfolio per position
    max_daily_loss: float = 0.05     # Max 5% daily loss
    max_drawdown: float = 0.1        # Max 10% drawdown
    risk_model: RiskModel = RiskModel.FIXED_PERCENTAGE
    stop_loss_percentage: float = 0.05  # 5% stop loss
    take_profit_percentage: float = 0.1  # 10% take profit
    max_open_positions: int = 5
    max_correlation: float = 0.7     # Max correlation between positions

class RiskManager:
    """Risk management system"""

    def __init__(self, config: RiskConfig):
        self.config = config
        self.daily_pnl = Decimal('0')
        self.daily_start_value = None

    def calculate_position_size(
        self,
        portfolio: Portfolio,
        signal: Signal,
        volatility: Optional[float] = None
    ) -> Decimal:
        """Calculate appropriate position size based on risk management rules"""

        # Check if we can open more positions
        if len(portfolio.positions) >= self.config.max_open_positions:
            log.warning("Maximum open positions reached")
            return Decimal('0')

        # Check daily loss limit
        if self._check_daily_loss_limit(portfolio):
            log.warning("Daily loss limit reached")
            return Decimal('0')

        # Calculate base position size
        if self.config.risk_model == RiskModel.FIXED_PERCENTAGE:
            position_size = self._calculate_fixed_percentage_size(portfolio, signal)
        elif self.config.risk_model == RiskModel.KELLY_CRITERION:
            position_size = self._calculate_kelly_size(portfolio, signal, volatility)
        else:  # FIXED_AMOUNT
            position_size = self._calculate_fixed_amount_size(portfolio)

        # Apply maximum position size limit
        max_position_value = portfolio.total_value * Decimal(str(self.config.max_position_size))
        max_quantity = max_position_value / signal.price

        return min(position_size, max_quantity)

    def _calculate_fixed_percentage_size(
        self,
        portfolio: Portfolio,
        signal: Signal
    ) -> Decimal:
        """Calculate position size using fixed percentage of portfolio"""
        risk_amount = portfolio.total_value * Decimal(str(self.config.max_portfolio_risk))
        stop_loss_amount = signal.price * Decimal(str(self.config.stop_loss_percentage))

        if stop_loss_amount == 0:
            return Decimal('0')

        quantity = risk_amount / stop_loss_amount
        return quantity

    def _calculate_kelly_size(
        self,
        portfolio: Portfolio,
        signal: Signal,
        volatility: Optional[float]
    ) -> Decimal:
        """Calculate position size using Kelly Criterion"""
        if not volatility:
            # Fall back to fixed percentage
            return self._calculate_fixed_percentage_size(portfolio, signal)

        # Simplified Kelly calculation
        # In practice, this would use win rate and win/loss ratio
        win_rate = 0.55  # Assume 55% win rate
        win_loss_ratio = 2.0  # Assume 2:1 win/loss ratio

        kelly_percentage = win_rate - ((1 - win_rate) / win_loss_ratio)
        kelly_percentage = max(0, min(kelly_percentage, 0.1))  # Cap at 10%

        risk_amount = portfolio.total_value * Decimal(str(kelly_percentage))
        quantity = risk_amount / signal.price

        return quantity

    def _calculate_fixed_amount_size(self, portfolio: Portfolio) -> Decimal:
        """Calculate fixed amount position size"""
        # Fixed $1000 per position (example)
        fixed_amount = Decimal('1000')
        return fixed_amount / portfolio.total_value * portfolio.total_value

    def should_close_position(
        self,
        position: Position,
        current_price: Decimal
    ) -> tuple[bool, str]:
        """Check if position should be closed based on risk rules"""

        # Stop loss check
        stop_loss_price = position.average_price * (1 - Decimal(str(self.config.stop_loss_percentage)))
        if current_price <= stop_loss_price:
            return True, "stop_loss"

        # Take profit check
        take_profit_price = position.average_price * (1 + Decimal(str(self.config.take_profit_percentage)))
        if current_price >= take_profit_price:
            return True, "take_profit"

        return False, ""

    def check_portfolio_risk(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Check overall portfolio risk metrics"""

        risk_status = {
            "within_limits": True,
            "warnings": [],
            "breaches": []
        }

        # Check drawdown
        if portfolio.total_pnl < 0:
            drawdown = abs(float(portfolio.total_pnl)) / float(portfolio.total_value + abs(portfolio.total_pnl))
            if drawdown > self.config.max_drawdown:
                risk_status["breaches"].append(f"Drawdown limit breached: {drawdown:.2%}")
                risk_status["within_limits"] = False

        # Check daily loss
        if self._check_daily_loss_limit(portfolio):
            risk_status["breaches"].append("Daily loss limit reached")
            risk_status["within_limits"] = False

        # Check position concentration
        for symbol, position in portfolio.positions.items():
            position_weight = float(position.market_value) / float(portfolio.total_value)
            if position_weight > self.config.max_position_size:
                risk_status["warnings"].append(f"Position {symbol} exceeds size limit: {position_weight:.2%}")

        return risk_status

    def _check_daily_loss_limit(self, portfolio: Portfolio) -> bool:
        """Check if daily loss limit is reached"""
        if self.daily_start_value is None:
            self.daily_start_value = portfolio.total_value
            return False

        daily_loss = (self.daily_start_value - portfolio.total_value) / self.daily_start_value
        return daily_loss >= self.config.max_daily_loss

    def reset_daily_pnl(self):
        """Reset daily P&L tracking"""
        self.daily_pnl = Decimal('0')
        self.daily_start_value = None

class PortfolioRebalancer:
    """Portfolio rebalancing logic"""

    def __init__(self, target_allocations: Dict[str, float]):
        self.target_allocations = target_allocations

    def calculate_rebalance_trades(
        self,
        portfolio: Portfolio
    ) -> List[Dict[str, Any]]:
        """Calculate trades needed to rebalance portfolio"""

        trades = []
        total_value = float(portfolio.total_value)

        # Calculate current allocations
        current_allocations = {}
        for symbol, position in portfolio.positions.items():
            current_allocations[symbol] = float(position.market_value) / total_value

        # Calculate cash allocation
        cash_allocation = float(portfolio.cash) / total_value
        current_allocations["CASH"] = cash_allocation

        # Calculate required trades
        for symbol, target_alloc in self.target_allocations.items():
            current_alloc = current_allocations.get(symbol, 0)
            alloc_diff = target_alloc - current_alloc

            if abs(alloc_diff) > 0.01:  # Rebalance if difference > 1%
                trade_value = alloc_diff * total_value

                if symbol in portfolio.positions:
                    current_quantity = float(portfolio.positions[symbol].quantity)
                    current_price = float(portfolio.positions[symbol].current_price)

                    if trade_value > 0:  # Buy more
                        additional_quantity = trade_value / current_price
                        trades.append({
                            "symbol": symbol,
                            "action": "BUY",
                            "quantity": additional_quantity
                        })
                    else:  # Sell some
                        sell_quantity = abs(trade_value) / current_price
                        sell_quantity = min(sell_quantity, current_quantity)
                        trades.append({
                            "symbol": symbol,
                            "action": "SELL",
                            "quantity": sell_quantity
                        })

        return trades