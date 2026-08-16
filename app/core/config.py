import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    API_ID: int = int(os.getenv("API_ID", 0))
    API_HASH: str = os.getenv("API_HASH", "")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 5))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    
    LINKS_PER_PAGE: int = int(os.getenv("LINKS_PER_PAGE", 20))
    CACHE_TTL_MINUTES: int = int(os.getenv("CACHE_TTL_MINUTES", 30))
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", 3))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", 5))
    WORKER_CONCURRENCY: int = int(os.getenv("WORKER_CONCURRENCY", 3))
    GLOBAL_RATE_LIMIT: int = int(os.getenv("GLOBAL_RATE_LIMIT", 50))
    PER_USER_RATE_LIMIT: int = int(os.getenv("PER_USER_RATE_LIMIT", 15))
    TEMPORARY_EXPORT_EXPIRY_HOURS: int = int(os.getenv("TEMPORARY_EXPORT_EXPIRY_HOURS", 24))
    LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", 30))
    MAX_MESSAGES_PER_SCAN: int = int(os.getenv("MAX_MESSAGES_PER_SCAN", 50000))
    MAX_LINKS_PER_WALLET: int = int(os.getenv("MAX_LINKS_PER_WALLET", 5000))
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "")

settings = Settings()
