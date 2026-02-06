"""
Logging configuration module for the application.
Provides centralized logging setup with structured logging, rotation, and formatting.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_logs: bool = False,
) -> None:
    """
    Setup application logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        json_logs: Whether to use JSON formatting
    """
    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if json_logs or settings.is_production:
        console_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        if json_logs or settings.is_production:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt=settings.LOG_FORMAT,
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {log_level}, "
        f"Environment: {settings.ENVIRONMENT}, "
        f"File: {log_file if log_file else 'None'}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context to logs."""

    def process(self, msg, kwargs):
        """Process log message with additional context."""
        # Add context from extra dict
        if self.extra:
            for key, value in self.extra.items():
                kwargs.setdefault("extra", {})[key] = value
        return msg, kwargs


def get_context_logger(name: str, **context) -> LoggerAdapter:
    """
    Get a logger with additional context.

    Args:
        name: Logger name
        **context: Additional context to include in all log messages

    Returns:
        LoggerAdapter instance with context

    Example:
        logger = get_context_logger(__name__, user_id="123", request_id="abc")
        logger.info("Processing request")  # Will include user_id and request_id
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, context)
