"""
Data models and types for the trading system.
Defines the core data structures used throughout the platform.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pydantic import BaseModel

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NO_SIGNAL = "NO_SIGNAL"

@dataclass
class OHLCV:
    """OHLCV data point"""
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "open": float(self.open),
            "high": float(self.high),
            "low": float(self.low),
            "close": float(self.close),
            "volume": self.volume
        }

@dataclass
class Order:
    """Trading order"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    order_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Position:
    """Portfolio position"""
    symbol: str
    quantity: Decimal
    average_price: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal = Decimal('0')

@dataclass
class Portfolio:
    """Portfolio summary"""
    total_value: Decimal
    cash: Decimal
    positions: Dict[str, Position] = field(default_factory=dict)
    total_pnl: Decimal = Decimal('0')
    daily_pnl: Decimal = Decimal('0')

@dataclass
class Trade:
    """Executed trade"""
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    timestamp: datetime
    commission: Decimal = Decimal('0')
    pnl: Optional[Decimal] = None

@dataclass
class Signal:
    """Trading signal"""
    symbol: str
    signal_type: SignalType
    timestamp: datetime
    price: Decimal
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IndicatorData:
    """Technical indicator data"""
    name: str
    symbol: str
    timestamp: datetime
    value: Union[float, Dict[str, float]]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BacktestResult:
    """Backtesting result"""
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: Decimal
    final_capital: Decimal
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Trade] = field(default_factory=list)
    portfolio_values: List[Dict[str, Any]] = field(default_factory=list)

# Pydantic models for API
class OHLCVModel(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class SignalModel(BaseModel):
    symbol: str
    signal_type: str
    timestamp: datetime
    price: float
    confidence: float = 1.0

class PortfolioModel(BaseModel):
    total_value: float
    cash: float
    positions: Dict[str, Dict[str, Any]]
    total_pnl: float
    daily_pnl: float

class BacktestRequest(BaseModel):
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    parameters: Dict[str, Any] = field(default_factory=dict)