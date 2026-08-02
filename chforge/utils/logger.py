"""
Logging utilities for CHForge
"""

import logging
import sys


def setup_logger(name: str = "chforge", level: str = "INFO") -> logging.Logger:
    """Setup and configure logger"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with safe stdout
    try:
        console_handler = logging.StreamHandler(sys.stdout or None)
        console_handler.setLevel(getattr(logging, level.upper()))

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    except (AttributeError, TypeError):
        # Fallback: no console handler
        pass

    return logger


# Default logger instance
logger = setup_logger()


def get_logger(name: str = "chforge") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)