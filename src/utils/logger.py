"""Centralized logging configuration."""
import logging
import sys

def setup_logger(name: str = "restaurant_booking") -> logging.Logger:
    """Setup logger that outputs to stderr (always captured)."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stderr)  # Use stderr instead of stdout
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Global logger instance
logger = setup_logger()
