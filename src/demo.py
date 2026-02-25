#!/usr/bin/env python3
"""
Demo script for the Enterprise Trading System.
Shows how to use the various components of the platform.
"""

import asyncio
from datetime import datetime, timedelta
from trading_system.data.providers import DataProviderFactory
from trading_system.strategies.strategies import StrategyFactory, StrategyConfig
from trading_system.backtesting.engine import BacktestRunner
from trading_system.core.logging import setup_logging

async def main():
    """Main demo function"""
    print("Enterprise Trading System Demo")
    print("=" * 50)

    # Setup logging
    setup_logging(level="INFO")

    try:
        # Initialize data provider
        print("Initializing data provider...")
        data_provider = DataProviderFactory.create_provider("yahoo_finance")

        # Get some sample data
        print("Fetching sample data for AAPL...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        ohlcv_data = await data_provider.get_historical_data("AAPL", start_date, end_date)
        print(f"Downloaded {len(ohlcv_data)} data points for AAPL")

        # Get current price
        current_price = await data_provider.get_current_price("AAPL")
        print(f"Current AAPL price: ${current_price:.2f}")

        # Create and test strategies
        print("\nTesting Trading Strategies...")

        strategies_to_test = [
            ("sma_crossover", {"short_period": 5, "long_period": 20}),
            ("rsi", {"rsi_period": 14, "oversold": 30, "overbought": 70}),
            ("macd", {}),
        ]

        for strategy_name, params in strategies_to_test:
            print(f"\nTesting {strategy_name} strategy...")

            # Create strategy
            config = StrategyConfig(
                name=strategy_name,
                symbol="AAPL",
                parameters=params
            )

            strategy = StrategyFactory.create_strategy(strategy_name, config, data_provider)

            # Initialize and generate signals
            await strategy.initialize()
            signals = await strategy.generate_signals(ohlcv_data[-50:])  # Last 50 data points

            print(f"   Generated {len(signals)} signals")
            for signal in signals[-3:]:  # Show last 3 signals
                print(f"   {signal.timestamp.strftime('%Y-%m-%d')}: {signal.signal_type.value} at ${signal.price:.2f}")

        # Run backtest comparison
        print("\nRunning Backtest Comparison...")
        runner = BacktestRunner(data_provider)

        backtest_start = end_date - timedelta(days=365)
        backtest_end = end_date

        results = await runner.compare_strategies(
            ["sma_crossover", "rsi", "macd"],
            "AAPL",
            backtest_start,
            backtest_end,
            100000
        )

        print("\nBacktest Results:")
        print("-" * 80)

        for strategy_name, result in results.items():
            print(f"   {strategy_name}: {result.total_return:.1%} return, {len(result.trades)} trades")
        # Find best performing strategy
        best_strategy = max(results.items(), key=lambda x: x[1].total_return)
        print(f"\nBest performing strategy: {best_strategy[0]} with {best_strategy[1].total_return:.1%} return")

        print("\nDemo completed successfully!")
        print("\nNext steps:")
        print("   • Configure your API keys in config/config.yaml")
        print("   • Run the web API: python -m trading_system.trading.api")
        print("   • Use the CLI: trading-system --help")
        print("   • Start backtesting: trading-system backtest rsi AAPL")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())