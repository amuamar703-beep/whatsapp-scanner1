#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import init_db, engine
from app.database.models import *
from app.core.config import settings
from app.core.logging import logger

def main():
    logger.info("Initializing database...")
    
    try:
        init_db()
        logger.info("Database tables created successfully!")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()