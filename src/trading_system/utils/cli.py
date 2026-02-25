"""
Command Line Interface for the Trading System.
Provides CLI commands for backtesting, live trading, and system management.
"""

import click
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

from ..core.config import config
from ..core.logging import setup_logging
from ..data.providers import DataProviderFactory
from ..strategies.strategies import StrategyFactory, StrategyConfig
from ..backtesting.engine import BacktestRunner
from ..core.logging import get_logger

log = get_logger(__name__)

@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
@click.option('--config-file', default=None, help='Configuration file path')
def cli(log_level: str, config_file: str):
    """Enterprise Trading System CLI"""
    setup_logging(level=log_level)

    if config_file:
        # Load custom config if provided
        pass

    click.echo(f"Trading System CLI v2.0.0")
    click.echo(f"Environment: {config.environment.value}")

@cli.command()
@click.argument('strategy_name')
@click.argument('symbol')
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD)')
@click.option('--capital', default=100000, type=float, help='Initial capital')
@click.option('--output', default=None, help='Output file for results')
@click.option('--parameters', default=None, help='Strategy parameters as JSON string')
def backtest(strategy_name: str, symbol: str, start_date: str, end_date: str,
            capital: float, output: str, parameters: str):
    """Run backtest for a trading strategy"""

    # Parse dates
    if not start_date:
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start_date, '%Y-%m-%d')

    if not end_date:
        end = datetime.now()
    else:
        end = datetime.strptime(end_date, '%Y-%m-%d')

    # Parse parameters
    strategy_params = {}
    if parameters:
        try:
            strategy_params = json.loads(parameters)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in parameters")
            return

    async def run_backtest():
        try:
            # Initialize data provider
            data_provider = DataProviderFactory.create_provider("yahoo_finance")
            runner = BacktestRunner(data_provider)

            click.echo(f"Running backtest for {strategy_name} on {symbol}")
            click.echo(f"Period: {start.date()} to {end.date()}")
            click.echo(f"Initial capital: ${capital:,.2f}")

            # Run backtest
            result = await runner.run_strategy_backtest(
                strategy_name, symbol, start, end, capital, strategy_params
            )

            # Display results
            click.echo("\n" + "="*50)
            click.echo("BACKTEST RESULTS")
            click.echo("="*50)
            click.echo(f"Strategy: {result.strategy_name}")
            click.echo(f"Symbol: {result.symbol}")
            click.echo(f"Initial Capital: ${result.initial_capital:,.2f}")
            click.echo(f"Final Capital: ${result.final_capital:,.2f}")
            click.echo(f"Total Return: {result.total_return:.2%}")
            click.echo(f"Annualized Return: {result.annualized_return:.2%}")
            click.echo(f"Max Drawdown: {result.max_drawdown:.2%}")
            click.echo(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
            click.echo(f"Total Trades: {len(result.trades)}")

            # Save results if output file specified
            if output:
                output_path = Path(output)
                with open(output_path, 'w') as f:
                    json.dump({
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
                        "trades": [trade.__dict__ for trade in result.trades],
                        "portfolio_values": result.portfolio_values
                    }, f, indent=2, default=str)

                click.echo(f"\nResults saved to {output_path}")

        except Exception as e:
            click.echo(f"Error running backtest: {e}", err=True)

    asyncio.run(run_backtest())

@cli.command()
@click.argument('strategies', nargs=-1)
@click.argument('symbol')
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD)')
@click.option('--capital', default=100000, type=float, help='Initial capital')
def compare(strategies: tuple, symbol: str, start_date: str, end_date: str, capital: float):
    """Compare multiple trading strategies"""

    if len(strategies) < 2:
        click.echo("Error: Need at least 2 strategies to compare")
        return

    # Parse dates
    if not start_date:
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start_date, '%Y-%m-%d')

    if not end_date:
        end = datetime.now()
    else:
        end = datetime.strptime(end_date, '%Y-%m-%d')

    async def run_comparison():
        try:
            # Initialize data provider
            data_provider = DataProviderFactory.create_provider("yahoo_finance")
            runner = BacktestRunner(data_provider)

            click.echo(f"Comparing strategies: {', '.join(strategies)}")
            click.echo(f"Symbol: {symbol}")
            click.echo(f"Period: {start.date()} to {end.date()}")
            click.echo(f"Initial capital: ${capital:,.2f}")

            # Run comparison
            results = await runner.compare_strategies(
                list(strategies), symbol, start, end, capital
            )

            # Display comparison table
            click.echo("\n" + "="*80)
            click.echo("STRATEGY COMPARISON")
            click.echo("="*80)
            click.echo("<20")
            click.echo("-"*80)

            for strategy_name, result in results.items():
                click.echo("<20")

        except Exception as e:
            click.echo(f"Error comparing strategies: {e}", err=True)

    asyncio.run(run_comparison())

@cli.command()
@click.argument('strategy_name')
@click.argument('symbol')
@click.option('--parameters', default=None, help='Strategy parameters as JSON string')
def signals(strategy_name: str, symbol: str, parameters: str):
    """Generate trading signals for a strategy"""

    # Parse parameters
    strategy_params = {}
    if parameters:
        try:
            strategy_params = json.loads(parameters)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in parameters")
            return

    async def generate_signals():
        try:
            # Initialize data provider
            data_provider = DataProviderFactory.create_provider("yahoo_finance")

            # Create strategy
            config = StrategyConfig(
                name=strategy_name,
                symbol=symbol,
                parameters=strategy_params
            )

            strategy = StrategyFactory.create_strategy(strategy_name, config, data_provider)

            # Initialize and generate signals
            await strategy.initialize()

            # Get recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            historical_data = await data_provider.get_historical_data(symbol, start_date, end_date)

            if not historical_data:
                click.echo(f"No data available for {symbol}")
                return

            signals = await strategy.generate_signals(historical_data)

            click.echo(f"Generated {len(signals)} signals for {strategy_name} on {symbol}")

            for signal in signals:
                click.echo(f"  {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - "
                          f"{signal.signal_type.value} at ${signal.price:.2f} "
                          f"(confidence: {signal.confidence:.2f})")

        except Exception as e:
            click.echo(f"Error generating signals: {e}", err=True)

    asyncio.run(generate_signals())

@cli.command()
@click.argument('symbol')
@click.option('--start-date', default=None, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', default=None, help='End date (YYYY-MM-DD)')
@click.option('--output', default=None, help='Output file for data')
def data(symbol: str, start_date: str, end_date: str, output: str):
    """Download historical market data"""

    # Parse dates
    if not start_date:
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start_date, '%Y-%m-%d')

    if not end_date:
        end = datetime.now()
    else:
        end = datetime.strptime(end_date, '%Y-%m-%d')

    async def download_data():
        try:
            # Initialize data provider
            data_provider = DataProviderFactory.create_provider("yahoo_finance")

            click.echo(f"Downloading data for {symbol} from {start.date()} to {end.date()}")

            # Get data
            ohlcv_data = await data_provider.get_historical_data(symbol, start, end)

            click.echo(f"Downloaded {len(ohlcv_data)} data points")

            if output:
                # Save to file
                output_path = Path(output)
                with open(output_path, 'w') as f:
                    json.dump([ohlcv.to_dict() for ohlcv in ohlcv_data], f, indent=2, default=str)
                click.echo(f"Data saved to {output_path}")
            else:
                # Display sample
                click.echo("\nSample data:")
                for i, ohlcv in enumerate(ohlcv_data[:5]):
                    click.echo(f"  {ohlcv.timestamp.date()}: O={ohlcv.open:.2f} H={ohlcv.high:.2f} "
                              f"L={ohlcv.low:.2f} C={ohlcv.close:.2f} V={ohlcv.volume}")

        except Exception as e:
            click.echo(f"Error downloading data: {e}", err=True)

    asyncio.run(download_data())

@cli.command()
def list_strategies():
    """List available trading strategies"""

    strategies = [
        ("sma_crossover", "Simple Moving Average Crossover"),
        ("rsi", "RSI-based Strategy"),
        ("macd", "MACD Crossover Strategy"),
        ("multi_indicator", "Multi-Indicator Strategy")
    ]

    click.echo("Available Strategies:")
    click.echo("-" * 40)
    for name, description in strategies:
        click.echo(f"  {name:<15} - {description}")

if __name__ == '__main__':
    cli()