"""
Logging utilities for GalacticNeighborsFinder.

Provides centralized logging configuration and utilities.
"""

import logging
from typing import Optional
from pathlib import Path

from gnf.constants import DEFAULT_LOG_LEVEL, LOG_FORMAT


def setup_logger(
    name: str,
    level: str = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up and configure a logger with console and optional file output.

    Parameters
    ----------
    name : str
        Name of the logger (typically __name__).
    level : str, optional
        Logging level as string (default: DEFAULT_LOG_LEVEL).
    log_file : str, optional
        Path to log file. If None, only console output is configured.

    Returns
    -------
    logging.Logger
        Configured logger instance.

    Examples
    --------
    >>> logger = setup_logger(__name__)
    >>> logger.info("Processing started")
    >>> logger = setup_logger(__name__, log_file="output.log")
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Set logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
