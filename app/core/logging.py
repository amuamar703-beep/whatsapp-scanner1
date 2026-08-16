import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

try:
    from app.core.config import settings
except ImportError:
    # Fallback for when config is not available
    class DummySettings:
        LOG_LEVEL = "INFO"
        LOG_FILE = "logs/app.log"
    settings = DummySettings()

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

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, getattr(settings, 'LOG_LEVEL', 'INFO'), logging.INFO))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    log_file = getattr(settings, 'LOG_FILE', 'logs/app.log')
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = RotatingFileHandler(
                log_file,
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
