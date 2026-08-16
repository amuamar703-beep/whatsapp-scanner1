import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

from app.core.config import settings

class SensitiveDataFilter(logging.Filter):
    def __init__(self):
        self.sensitive_patterns = [
            "session_encrypted",
            "session_string",
            "BOT_TOKEN",
            "API_HASH",
            "SECRET_KEY",
            "ENCRYPTION_KEY",
            "password",
            "token",
            "authorization",
            "bearer"
        ]

    def filter(self, record):
        if hasattr(record, 'msg'):
            for pattern in self.sensitive_patterns:
                if pattern in str(record.msg).lower():
                    record.msg = "SENSITIVE_DATA_REDACTED"
                    return True
        return True

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m'
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    if settings.LOG_FILE:
        try:
            file_handler = RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=10485760,
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(SensitiveDataFilter())
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to create log file handler: {e}")

    return logger

logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

class LoggerContext:
    def __init__(self, logger: logging.Logger, context: dict):
        self.logger = logger
        self.context = context
        self.original_extra = getattr(logger, 'extra', {})

    def __enter__(self):
        self.logger.extra = {**self.logger.extra, **self.context}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.extra = self.original_extra

def log_function_call(logger: logging.Logger):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise

        def sync_wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator