import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import logger
from app.core.config import settings
from app.database.database import init_db
from app.bot.dispatcher import dp, bot, on_startup, on_shutdown
from app.workers.queue import QueueManager
from app.workers import (
    ScanWorker,
    AnalysisWorker,
    ExportWorker,
    CleanupWorker,
    RescanWorker
)
from app.userbot import UserbotManager

async def main():
    logger.info("Starting WhatsApp Link Scanner...")
    logger.info(f"Database URL: {settings.DATABASE_URL[:50]}...")

    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    queue_manager = QueueManager()
    try:
        await queue_manager.connect()
        logger.info("Queue manager connected")
    except Exception as e:
        logger.error(f"Failed to connect to queue: {e}")
        return

    userbot_manager = UserbotManager()

    scan_worker = ScanWorker(queue_manager, userbot_manager)
    analysis_worker = AnalysisWorker(queue_manager)
    export_worker = ExportWorker(queue_manager)
    cleanup_worker = CleanupWorker(queue_manager)
    rescan_worker = RescanWorker(queue_manager)

    try:
        await scan_worker.start()
        await analysis_worker.start()
        await export_worker.start()
        await cleanup_worker.start()
        await rescan_worker.start()
        logger.info("All workers started")
    except Exception as e:
        logger.error(f"Failed to start workers: {e}")
        return

    await on_startup()

    try:
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        await scan_worker.stop()
        await analysis_worker.stop()
        await export_worker.stop()
        await cleanup_worker.stop()
        await rescan_worker.stop()
        await queue_manager.disconnect()
        await userbot_manager.disconnect_all()
        await on_shutdown()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
