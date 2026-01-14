"""
Logging utility for ARIA.

Provides file and console logging with rotation support.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


# Global logger instance
_logger = None


def get_log_dir() -> Path:
    """Get the log directory path."""
    # Use project directory for portability
    current = Path(__file__).resolve()
    project_root = current.parent.parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(name: str = "ARIA", level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up and return the application logger.
    
    Args:
        name: Logger name
        level: Logging level (default: DEBUG)
    
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    
    # Prevent duplicate handlers
    if _logger.handlers:
        return _logger
    
    # Log format
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    # File handler (all levels, with rotation)
    log_dir = get_log_dir()
    log_file = log_dir / "aria.log"
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    _logger.info(f"Logger initialized. Log file: {log_file}")
    
    return _logger


def get_logger() -> logging.Logger:
    """
    Get the application logger.
    
    Returns:
        Logger instance (creates one if not exists)
    """
    if _logger is None:
        return setup_logger()
    return _logger


# Convenience functions
def debug(msg: str, *args, **kwargs):
    """Log debug message."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log info message."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log warning message."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log error message."""
    get_logger().error(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """Log exception with traceback."""
    get_logger().exception(msg, *args, **kwargs)
