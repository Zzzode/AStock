"""Unified logging configuration"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    console: bool = True,
) -> None:
    """Configure logging system

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name, None means no file output
        log_dir: Log file directory
        console: Whether to output to console
    """
    # Get root logger
    root_logger = logging.getLogger("astock")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_dir) / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str = "astock") -> logging.Logger:
    """Get logger

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    # Ensure astock prefix
    if not name.startswith("astock"):
        name = f"astock.{name}"
    return logging.getLogger(name)


# Default configuration
setup_logging()
