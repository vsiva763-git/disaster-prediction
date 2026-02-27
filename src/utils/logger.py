"""
Logger Configuration
Centralized logging setup
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_dir: str = 'logs', level: str = 'INFO'):
    """
    Setup centralized logging configuration
    
    Args:
        log_dir: Directory for log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # File logger - all logs
    logger.add(
        Path(log_dir) / "tsunami_system.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="30 days",
        compression="zip"
    )
    
    # File logger - errors only
    logger.add(
        Path(log_dir) / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="zip"
    )
    
    # File logger - alerts only
    logger.add(
        Path(log_dir) / "alerts.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="WARNING",
        filter=lambda record: "ALERT" in record["message"] or "WARNING" in record["message"],
        rotation="10 MB",
        retention="90 days"
    )
    
    logger.success("Logging configured successfully")
    
    return logger
