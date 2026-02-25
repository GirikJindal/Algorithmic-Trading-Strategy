# Enterprise Algorithmic Trading System

A professional-grade algorithmic trading platform built with Python, featuring multiple data providers, advanced strategies, comprehensive backtesting, risk management, and a web API.

## 🚀 Features

### Core Features
- **Multiple Data Providers**: Alpha Vantage, Yahoo Finance, and Polygon support
- **Advanced Strategies**: SMA, RSI, MACD, and Multi-Indicator strategies
- **Comprehensive Backtesting**: Performance metrics, risk analysis, and comparison tools
- **Risk Management**: Position sizing, stop losses, and portfolio risk controls
- **Web API**: RESTful API with FastAPI for integration
- **CLI Interface**: Command-line tools for all operations

### Enterprise Features
- **Production Ready**: Logging, configuration management, error handling
- **Scalable Architecture**: Modular design with dependency injection
- **Security**: API key management and secure configuration
- **Monitoring**: Health checks and performance monitoring
- **Documentation**: Comprehensive API docs and user guides

## 📋 Requirements

- Python 3.8+
- pip
- git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/trading-system.git
   cd trading-system
   ```

2. **Create virtual environment** (⚠️ **DO NOT** push venv to repository)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the package**
   ```bash
   pip install -e .
   ```

## 📁 Project Structure & Best Practices

### .gitignore
The project includes a comprehensive `.gitignore` file that excludes:
- Virtual environments (`venv/`, `env/`, etc.)
- Python cache files (`__pycache__/`, `*.pyc`)
- Sensitive configuration (`config/config.yaml`, `.env`)
- Logs and temporary files
- IDE and OS specific files

**⚠️ Important**: Never commit virtual environments, API keys, or sensitive data to version control.

### Development Setup
For detailed development setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

## ⚙️ Configuration

Create a configuration file `config/config.yaml`:

```yaml
environment: development
debug: true

data_provider:
  alpha_vantage_api_key: "YOUR_API_KEY"
  cache_enabled: true
  cache_ttl: 300

trading:
  alpaca_api_key: "YOUR_ALPACA_KEY"
  alpaca_secret_key: "YOUR_ALPACA_SECRET"
  alpaca_base_url: "https://paper-api.alpaca.markets"

backtesting:
  initial_capital: 100000
  commission: 0.001
  slippage: 0.0005
```

Or set environment variables:
```bash
export ALPHA_VANTAGE_API_KEY="your_key_here"
export ALPACA_API_KEY="your_key_here"
export ALPACA_SECRET_KEY="your_secret_here"
```

## 🚀 Usage

### Command Line Interface

**Run a backtest:**
```bash
trading-system backtest sma_crossover AAPL --start-date 2023-01-01 --end-date 2023-12-31 --capital 100000
```

**Compare strategies:**
```bash
trading-system compare sma_crossover rsi macd AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

**Generate signals:**
```bash
trading-system signals rsi AAPL
```

**Download data:**
```bash
trading-system data AAPL --start-date 2023-01-01 --end-date 2023-12-31 --output aapl_data.json
```

### Web API

**Start the API server:**
```bash
python -m trading_system.trading.api
```

The API will be available at `http://localhost:8000`

**API Endpoints:**

- `GET /` - API root
- `GET /health` - Health check
- `GET /strategies` - List available strategies
- `POST /strategies/{strategy}/signals` - Generate signals
- `POST /backtest` - Run backtest
- `POST /backtest/compare` - Compare strategies
- `GET /data/{symbol}` - Get historical data
- `GET /data/{symbol}/current` - Get current price

### Python API

```python
from trading_system.data.providers import DataProviderFactory
from trading_system.strategies.strategies import StrategyFactory, StrategyConfig
from trading_system.backtesting.engine import BacktestRunner
import asyncio

async def main():
    # Initialize data provider
    data_provider = DataProviderFactory.create_provider("yahoo_finance")

    # Create strategy
    config = StrategyConfig(
        name="rsi",
        symbol="AAPL",
        parameters={"rsi_period": 14, "oversold": 30, "overbought": 70}
    )
    strategy = StrategyFactory.create_strategy("rsi", config, data_provider)

    # Run backtest
    runner = BacktestRunner(data_provider)
    result = await runner.run_strategy_backtest(
        "rsi", "AAPL",
        datetime(2023, 1, 1), datetime(2023, 12, 31),
        100000
    )

    print(f"Total Return: {result.total_return:.2%}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")

asyncio.run(main())
```

## 📊 Available Strategies

### 1. Simple Moving Average Crossover (`sma_crossover`)
- **Parameters:**
  - `short_period` (int): Short SMA period (default: 5)
  - `long_period` (int): Long SMA period (default: 20)
- **Logic:** Buy when short SMA crosses above long SMA, sell when it crosses below

### 2. RSI Strategy (`rsi`)
- **Parameters:**
  - `rsi_period` (int): RSI calculation period (default: 14)
  - `oversold` (int): Oversold threshold (default: 30)
  - `overbought` (int): Overbought threshold (default: 70)
- **Logic:** Buy when RSI < oversold, sell when RSI > overbought

### 3. MACD Strategy (`macd`)
- **Parameters:**
  - `fast_period` (int): Fast EMA period (default: 12)
  - `slow_period` (int): Slow EMA period (default: 26)
  - `signal_period` (int): Signal line period (default: 9)
- **Logic:** Buy when MACD crosses above signal line, sell when it crosses below

### 4. Multi-Indicator Strategy (`multi_indicator`)
- **Parameters:** None (uses default settings)
- **Logic:** Combines RSI, MACD, Bollinger Bands, and SMA for consensus signals

## 📈 Backtesting

The system provides comprehensive backtesting with:

- **Performance Metrics:**
  - Total return
  - Annualized return
  - Maximum drawdown
  - Sharpe ratio
  - Sortino ratio
  - Win rate
  - Profit factor

- **Risk Metrics:**
  - Value at Risk (VaR)
  - Expected Shortfall
  - Beta
  - Volatility

- **Trade Analysis:**
  - Trade history
  - P&L distribution
  - Holding periods
  - Win/loss streaks

## 🛡️ Risk Management

- **Position Sizing:** Fixed percentage, Kelly Criterion, or fixed amount
- **Stop Losses:** Percentage-based or volatility-based
- **Take Profits:** Target profit levels
- **Portfolio Limits:** Maximum drawdown, daily loss limits
- **Diversification:** Position concentration limits

## 🔧 Development

### Project Structure
```
src/trading_system/
├── core/              # Core functionality
│   ├── config.py     # Configuration management
│   ├── logging.py    # Logging system
│   └── models.py     # Data models
├── data/             # Data providers
│   └── providers.py  # Data provider implementations
├── strategies/       # Trading strategies
│   ├── indicators.py # Technical indicators
│   └── strategies.py # Strategy implementations
├── trading/          # Trading integration
│   └── api.py       # Web API
├── backtesting/      # Backtesting engine
│   └── engine.py    # Backtesting logic
├── risk/            # Risk management
│   └── management.py # Risk controls
└── utils/           # Utilities
    └── cli.py       # Command-line interface
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black src/

# Sort imports
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 📚 API Documentation

When running the API server, visit `http://localhost:8000/docs` for interactive API documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. It should not be used for actual trading without proper testing and risk assessment. Past performance does not guarantee future results. Trading involves substantial risk of loss.

## 🆘 Support

- **Documentation:** See the `docs/` directory
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

**Version:** 2.0.0
**Python Version:** 3.8+
**Maintainer:** Trading System Team
