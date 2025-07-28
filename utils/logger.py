"""
Logging utility for Ship Safety System Integration Platform
Provides structured logging for all system components.
"""

import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

def setup_logger():
    """Setup structured logging for the ship safety system."""
    
    # Remove default logger
    logger.remove()
    
    # Console logging with colors and formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File logging for system events
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "ship_safety_system_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Critical events log
    logger.add(
        log_dir / "critical_events_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days"
    )
    
    return logger 