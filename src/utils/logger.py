"""Centralized logging configuration for AgentCore Runtime."""
import logging
import sys
import os

# Force unbuffered output for CloudWatch
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

def setup_logger(name: str = "restaurant_booking") -> logging.Logger:
    """Setup logger for AgentCore Runtime (stdout/stderr only)."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Stdout handler for INFO and above (goes to CloudWatch automatically)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        stdout_handler.setFormatter(stdout_formatter)
        logger.addHandler(stdout_handler)
        
        # Stderr handler for warnings and errors (goes to CloudWatch automatically)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.setFormatter(stdout_formatter)
        logger.addHandler(stderr_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger

# Global logger instance
logger = setup_logger()
