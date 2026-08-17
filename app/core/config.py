import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    API_ID: int = 0
    API_HASH: str = ""
    
    DATABASE_URL: str = "postgresql://localhost:5432/db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = ""
    ENCRYPTION_KEY: str = ""
    
    LINKS_PER_PAGE: int = 20
    CACHE_TTL_MINUTES: int = 30
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5
    WORKER_CONCURRENCY: int = 3
    GLOBAL_RATE_LIMIT: int = 50
    PER_USER_RATE_LIMIT: int = 15
    TEMPORARY_EXPORT_EXPIRY_HOURS: int = 24
    LOG_RETENTION_DAYS: int = 30
    MAX_MESSAGES_PER_SCAN: int = 50000
    MAX_LINKS_PER_WALLET: int = 5000
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    ADMIN_IDS: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
