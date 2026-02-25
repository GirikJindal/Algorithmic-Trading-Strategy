"""
FastAPI web application for the trading system.
Provides REST API endpoints for trading operations, backtesting, and monitoring.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import uvicorn

from ..core.config import config
from ..core.models import (
    SignalModel, PortfolioModel, BacktestRequest,
    BacktestResult, SignalType
)
from ..data.providers import DataProviderFactory
from ..strategies.strategies import StrategyFactory, StrategyConfig
from ..backtesting.engine import BacktestRunner
from ..core.logging import get_logger

log = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Enterprise Trading System API",
    description="Professional algorithmic trading platform with backtesting and live trading capabilities",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_provider = None
backtest_runner = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global data_provider, backtest_runner

    try:
        # Initialize data provider
        data_provider = DataProviderFactory.create_provider("yahoo_finance")  # Default to Yahoo Finance
        backtest_runner = BacktestRunner(data_provider)
        log.info("Trading system API started successfully")
    except Exception as e:
        log.error(f"Failed to initialize services: {e}")
        raise

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Enterprise Trading System API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "data_provider": data_provider is not None,
            "backtest_runner": backtest_runner is not None
        }
    }

# Strategy endpoints
@app.get("/strategies")
async def list_strategies():
    """List available trading strategies"""
    strategies = [
        {
            "name": "sma_crossover",
            "description": "Simple Moving Average Crossover Strategy",
            "parameters": {
                "short_period": {"type": "int", "default": 5, "description": "Short SMA period"},
                "long_period": {"type": "int", "default": 20, "description": "Long SMA period"}
            }
        },
        {
            "name": "rsi",
            "description": "RSI-based Trading Strategy",
            "parameters": {
                "rsi_period": {"type": "int", "default": 14, "description": "RSI period"},
                "oversold": {"type": "int", "default": 30, "description": "Oversold threshold"},
                "overbought": {"type": "int", "default": 70, "description": "Overbought threshold"}
            }
        },
        {
            "name": "macd",
            "description": "MACD Crossover Strategy",
            "parameters": {
                "fast_period": {"type": "int", "default": 12, "description": "Fast EMA period"},
                "slow_period": {"type": "int", "default": 26, "description": "Slow EMA period"},
                "signal_period": {"type": "int", "default": 9, "description": "Signal line period"}
            }
        },
        {
            "name": "multi_indicator",
            "description": "Multi-Indicator Strategy",
            "parameters": {}
        }
    ]
    return {"strategies": strategies}

@app.post("/strategies/{strategy_name}/signals")
async def get_strategy_signals(
    strategy_name: str,
    symbol: str,
    parameters: Optional[Dict[str, Any]] = None
):
    """Get trading signals for a strategy"""
    try:
        # Create strategy config
        config = StrategyConfig(
            name=strategy_name,
            symbol=symbol,
            parameters=parameters or {}
        )

        # Create strategy
        strategy = StrategyFactory.create_strategy(strategy_name, config, data_provider)

        # Initialize and get signals
        await strategy.initialize()

        # Get recent data for signal generation
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days

        historical_data = await data_provider.get_historical_data(symbol, start_date, end_date)

        if not historical_data:
            raise HTTPException(status_code=404, detail="No data available for symbol")

        signals = await strategy.generate_signals(historical_data)

        # Convert to response format
        signal_responses = []
        for signal in signals:
            signal_responses.append({
                "symbol": signal.symbol,
                "signal_type": signal.signal_type.value,
                "timestamp": signal.timestamp.isoformat(),
                "price": float(signal.price),
                "confidence": signal.confidence,
                "metadata": signal.metadata
            })

        return {"signals": signal_responses}

    except Exception as e:
        log.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Backtesting endpoints
@app.post("/backtest")
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """Run a backtest for a trading strategy"""
    try:
        # Parse dates
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))

        # Run backtest
        result = await backtest_runner.run_strategy_backtest(
            request.strategy_name,
            request.symbol,
            start_date,
            end_date,
            request.initial_capital,
            request.parameters
        )

        # Convert to response format
        response = {
            "strategy_name": result.strategy_name,
            "symbol": result.symbol,
            "start_date": result.start_date.isoformat(),
            "end_date": result.end_date.isoformat(),
            "initial_capital": result.initial_capital,
            "final_capital": result.final_capital,
            "total_return": result.total_return,
            "annualized_return": result.annualized_return,
            "max_drawdown": result.max_drawdown,
            "sharpe_ratio": result.sharpe_ratio,
            "total_trades": len(result.trades),
            "portfolio_values": result.portfolio_values
        }

        return response

    except Exception as e:
        log.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest/compare")
async def compare_strategies(
    strategies: List[str],
    symbol: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0
):
    """Compare multiple strategies"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        results = await backtest_runner.compare_strategies(
            strategies, symbol, start, end, initial_capital
        )

        # Convert results to response format
        comparison = {}
        for strategy_name, result in results.items():
            comparison[strategy_name] = {
                "total_return": result.total_return,
                "annualized_return": result.annualized_return,
                "max_drawdown": result.max_drawdown,
                "sharpe_ratio": result.sharpe_ratio,
                "total_trades": len(result.trades),
                "final_capital": result.final_capital
            }

        return {"comparison": comparison}

    except Exception as e:
        log.error(f"Error comparing strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Data endpoints
@app.get("/data/{symbol}")
async def get_market_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d"
):
    """Get historical market data"""
    try:
        if not start_date:
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))

        if not end_date:
            end = datetime.now()
        else:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        data = await data_provider.get_historical_data(symbol, start, end, interval)

        # Convert to response format
        response_data = []
        for ohlcv in data:
            response_data.append(ohlcv.to_dict())

        return {
            "symbol": symbol,
            "data": response_data,
            "count": len(response_data)
        }

    except Exception as e:
        log.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{symbol}/current")
async def get_current_price(symbol: str):
    """Get current price for a symbol"""
    try:
        price = await data_provider.get_current_price(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        log.error(f"Error fetching current price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoint
@app.get("/config")
async def get_system_config():
    """Get system configuration (sensitive data redacted)"""
    return {
        "environment": config.environment.value,
        "debug": config.debug,
        "data_provider": {
            "cache_enabled": config.data_provider.cache_enabled,
            "cache_ttl": config.data_provider.cache_ttl
        },
        "backtesting": {
            "initial_capital": float(config.backtesting.initial_capital),
            "commission": float(config.backtesting.commission),
            "slippage": float(config.backtesting.slippage)
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "trading_system.trading.api:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug
    )