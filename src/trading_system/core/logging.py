"""
Logging system for the trading platform.
Provides structured logging with different levels and outputs.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger

from .config import config

def setup_logging(
    level: Optional[str] = None,
    file_path: Optional[str] = None,
    format_string: Optional[str] = None
):
    """Setup logging configuration"""

    # Remove default handler
    logger.remove()

    # Use config values if not provided
    level = level or config.logging.level
    file_path = file_path or config.logging.file_path
    format_string = format_string or config.logging.format

    # Convert level string to loguru level
    level_map = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL"
    }
    log_level = level_map.get(level.upper(), "INFO")

    # Console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format=format_string,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # File handler
    if file_path:
        log_file = Path(file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            level=log_level,
            format=format_string,
            rotation=config.logging.max_file_size,
            retention=config.logging.retention,
            encoding="utf-8"
        )

    # Add extra context for trading operations
    return logger.bind(system="trading_platform")

# Global logger instance
log = setup_logging()

def get_logger(name: str):
    """Get a logger instance with the specified name"""
    return log.bind(module=name)