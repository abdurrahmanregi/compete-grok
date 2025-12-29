"""
CompeteGrok Logging Configuration Module.

This module provides structured logging setup for the CompeteGrok project,
including JSON formatting, console and file handlers, and appropriate log levels.
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        import datetime
        log_entry = {
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Set up structured logging for CompeteGrok.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str): Optional log file path. If None, logs to console only.

    Returns:
        logging.Logger: Root logger instance.
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # JSON formatter
    json_formatter = JSONFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all levels
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)

    return logger

# Convenience function to get logger for modules
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(name)

# Initialize default logging if this module is run directly
if __name__ == "__main__":
    log_file = f"logs/compete_grok_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging("DEBUG", log_file)
    logger = get_logger(__name__)
    logger.info("Logging initialized")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message", exc_info=True)