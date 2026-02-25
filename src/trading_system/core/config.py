"""
Configuration management for the trading system.
Supports multiple environments and secure credential management.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "trading_db"
    username: str = ""
    password: str = ""
    connection_pool_size: int = 10
    connection_timeout: int = 30

@dataclass
class DataProviderConfig:
    """Data provider configuration"""
    alpha_vantage_api_key: str = ""
    yahoo_finance_enabled: bool = True
    polygon_api_key: str = ""
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes

@dataclass
class TradingConfig:
    """Trading configuration"""
    broker: str = "alpaca"  # alpaca, interactive_brokers, etc.
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    max_position_size: float = 0.1  # Max 10% of portfolio
    max_daily_loss: float = 0.05  # Max 5% daily loss
    commission_per_trade: float = 0.0

@dataclass
class BacktestingConfig:
    """Backtesting configuration"""
    initial_capital: float = 100000.0
    commission: float = 0.001  # 0.1% per trade
    slippage: float = 0.0005  # 0.05% slippage
    benchmark_symbol: str = "SPY"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_path: str = "logs/trading_system.log"
    max_file_size: str = "10 MB"
    retention: str = "30 days"
    format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

@dataclass
class SystemConfig:
    """Main system configuration"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    timezone: str = "America/New_York"

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    data_provider: DataProviderConfig = field(default_factory=DataProviderConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    backtesting: BacktestingConfig = field(default_factory=BacktestingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

class ConfigManager:
    """Configuration manager with environment support"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._find_config_file()
        self.config = self._load_config()

    def _find_config_file(self) -> str:
        """Find configuration file in standard locations"""
        search_paths = [
            Path.cwd() / "config",
            Path.cwd(),
            Path.home() / ".trading_system"
        ]

        for path in search_paths:
            config_path = path / "config.yaml"
            if config_path.exists():
                return str(config_path)

        return str(Path.cwd() / "config" / "config.yaml")

    def _load_config(self) -> SystemConfig:
        """Load configuration from file and environment variables"""
        config = SystemConfig()

        # Load from YAML file if it exists
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                yaml_config = yaml.safe_load(f) or {}
                self._update_from_dict(config, yaml_config)

        # Override with environment variables
        self._load_from_env(config)

        return config

    def _update_from_dict(self, config: SystemConfig, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        # This would be implemented to recursively update the dataclass
        # For brevity, we'll use environment variables primarily
        pass

    def _load_from_env(self, config: SystemConfig):
        """Load configuration from environment variables"""
        # Database
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", config.database.port))
        config.database.database = os.getenv("DB_NAME", config.database.database)
        config.database.username = os.getenv("DB_USER", config.database.username)
        config.database.password = os.getenv("DB_PASSWORD", config.database.password)

        # Data Providers
        config.data_provider.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        config.data_provider.polygon_api_key = os.getenv("POLYGON_API_KEY", "")

        # Trading
        config.trading.alpaca_api_key = os.getenv("ALPACA_API_KEY", "")
        config.trading.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY", "")
        config.trading.alpaca_base_url = os.getenv("ALPACA_BASE_URL", config.trading.alpaca_base_url)

        # Environment
        env = os.getenv("TRADING_ENV", "development").lower()
        config.environment = Environment(env) if env in [e.value for e in Environment] else Environment.DEVELOPMENT
        config.debug = os.getenv("DEBUG", "false").lower() == "true"

    def get_config(self) -> SystemConfig:
        """Get the current configuration"""
        return self.config

    def save_config(self, config: SystemConfig):
        """Save configuration to file"""
        config_dict = self._config_to_dict(config)
        Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)

    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        # Implementation would convert dataclass to dict
        return {}

# Global configuration instance
config_manager = ConfigManager()
config = config_manager.get_config()