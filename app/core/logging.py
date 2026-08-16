import logging
import sys
import os
from logging.handlers import RotatingFileHandler
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
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for pattern in self.sensitive_patterns:
                if pattern.lower() in record.msg.lower():
                    record.msg = "SENSITIVE_DATA_REDACTED"
                    return True
        return True

def setup_logging():
    logger = logging.getLogger()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    if settings.LOG_FILE:
        try:
            log_dir = os.path.dirname(settings.LOG_FILE)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
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
