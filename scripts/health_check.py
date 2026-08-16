#!/usr/bin/env python3

import sys
import os
import requests
import redis
import psycopg2
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_database():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {e}"

def check_redis():
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return True, "Redis connection successful"
    except Exception as e:
        return False, f"Redis connection failed: {e}"

def check_telegram_bot():
    try:
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return True, f"Bot connected: @{data['result']['username']}"
        return False, "Bot connection failed"
    except Exception as e:
        return False, f"Bot connection error: {e}"

def main():
    print(f"=== Health Check: {datetime.now().isoformat()} ===")
    print("")
    
    checks = [
        ("Database", check_database),
        ("Redis", check_redis),
        ("Telegram Bot", check_telegram_bot)
    ]
    
    all_ok = True
    
    for name, check_func in checks:
        status, message = check_func()
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}: {message}")
        if not status:
            all_ok = False
    
    if all_ok:
        print("\n✅ All systems operational")
        sys.exit(0)
    else:
        print("\n❌ Some systems are not operational")
        sys.exit(1)

if __name__ == "__main__":
    main()