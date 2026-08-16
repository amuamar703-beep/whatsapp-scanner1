import os
from typing import Optional
from pydantic import BaseModel, Field

class Settings(BaseModel):
    BOT_TOKEN: str = Field(default="")
    API_ID: int = Field(default=0)
    API_HASH: str = Field(default="")
    
    DATABASE_URL: str = Field(default="postgresql://localhost:5432/db")
    DB_POOL_SIZE: int = Field(default=5)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_ECHO: bool = Field(default=False)
    
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    SECRET_KEY: str = Field(default="")
    ENCRYPTION_KEY: str = Field(default="")
    
    LINKS_PER_PAGE: int = Field(default=20)
    CACHE_TTL_MINUTES: int = Field(default=30)
    MAX_RETRY_ATTEMPTS: int = Field(default=3)
    RETRY_DELAY_SECONDS: int = Field(default=5)
    WORKER_CONCURRENCY: int = Field(default=3)
    GLOBAL_RATE_LIMIT: int = Field(default=50)
    PER_USER_RATE_LIMIT: int = Field(default=15)
    TEMPORARY_EXPORT_EXPIRY_HOURS: int = Field(default=24)
    LOG_RETENTION_DAYS: int = Field(default=30)
    MAX_MESSAGES_PER_SCAN: int = Field(default=50000)
    MAX_LINKS_PER_WALLET: int = Field(default=5000)
    
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    
    ADMIN_IDS: str = Field(default="")

def load_settings_from_env() -> Settings:
    """Load settings from environment variables"""
    return Settings(
        BOT_TOKEN=os.getenv("BOT_TOKEN", ""),
        API_ID=int(os.getenv("API_ID", 0)),
        API_HASH=os.getenv("API_HASH", ""),
        DATABASE_URL=os.getenv("DATABASE_URL", "postgresql://localhost:5432/db"),
        DB_POOL_SIZE=int(os.getenv("DB_POOL_SIZE", 5)),
        DB_MAX_OVERFLOW=int(os.getenv("DB_MAX_OVERFLOW", 10)),
        DB_ECHO=os.getenv("DB_ECHO", "false").lower() == "true",
        REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        SECRET_KEY=os.getenv("SECRET_KEY", ""),
        ENCRYPTION_KEY=os.getenv("ENCRYPTION_KEY", ""),
        LINKS_PER_PAGE=int(os.getenv("LINKS_PER_PAGE", 20)),
        CACHE_TTL_MINUTES=int(os.getenv("CACHE_TTL_MINUTES", 30)),
        MAX_RETRY_ATTEMPTS=int(os.getenv("MAX_RETRY_ATTEMPTS", 3)),
        RETRY_DELAY_SECONDS=int(os.getenv("RETRY_DELAY_SECONDS", 5)),
        WORKER_CONCURRENCY=int(os.getenv("WORKER_CONCURRENCY", 3)),
        GLOBAL_RATE_LIMIT=int(os.getenv("GLOBAL_RATE_LIMIT", 50)),
        PER_USER_RATE_LIMIT=int(os.getenv("PER_USER_RATE_LIMIT", 15)),
        TEMPORARY_EXPORT_EXPIRY_HOURS=int(os.getenv("TEMPORARY_EXPORT_EXPIRY_HOURS", 24)),
        LOG_RETENTION_DAYS=int(os.getenv("LOG_RETENTION_DAYS", 30)),
        MAX_MESSAGES_PER_SCAN=int(os.getenv("MAX_MESSAGES_PER_SCAN", 50000)),
        MAX_LINKS_PER_WALLET=int(os.getenv("MAX_LINKS_PER_WALLET", 5000)),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        LOG_FILE=os.getenv("LOG_FILE", "logs/app.log"),
        ADMIN_IDS=os.getenv("ADMIN_IDS", "")
    )

settings = load_settings_from_env()
