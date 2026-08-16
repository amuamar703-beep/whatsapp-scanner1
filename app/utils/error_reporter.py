import traceback
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.logging import logger
from app.core.config import settings

class ErrorReporter:
    @staticmethod
    def report_error(
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        job_id: Optional[str] = None
    ):
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "user_id": user_id,
            "job_id": job_id,
            "environment": "production"
        }

        logger.error(
            f"Error reported: {error_data['error_type']} - {error_data['error_message']}",
            extra=error_data
        )

        if settings.ADMIN_IDS:
            try:
                from aiogram import Bot
                bot = Bot(token=settings.BOT_TOKEN)
                admin_ids = [int(a.strip()) for a in settings.ADMIN_IDS.split(',') if a.strip()]
                
                for admin_id in admin_ids:
                    bot.send_message(
                        admin_id,
                        f"⚠️ خطأ في النظام\n\n"
                        f"النوع: {error_data['error_type']}\n"
                        f"الرسالة: {error_data['error_message']}\n"
                        f"المستخدم: {user_id}\n"
                        f"المهمة: {job_id}\n"
                        f"الوقت: {error_data['timestamp']}"
                    )
            except Exception:
                pass

    @staticmethod
    def report_warning(
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ):
        logger.warning(
            f"Warning: {message}",
            extra={
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
                "user_id": user_id
            }
        )

    @staticmethod
    def report_info(
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ):
        logger.info(
            f"Info: {message}",
            extra={
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
                "user_id": user_id
            }
        )

error_reporter = ErrorReporter()