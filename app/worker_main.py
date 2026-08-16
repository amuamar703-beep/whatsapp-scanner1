import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import logger
from app.core.config import settings
from app.database.database import init_db
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
    logger.info("Starting WhatsApp Link Scanner Workers...")

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

    workers = [scan_worker, analysis_worker, export_worker, cleanup_worker, rescan_worker]

    try:
        for worker in workers:
            await worker.start()
        logger.info("All workers started successfully!")
    except Exception as e:
        logger.error(f"Failed to start workers: {e}")
        return

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Workers stopped by user")
    finally:
        for worker in workers:
            await worker.stop()
        await queue_manager.disconnect()
        await userbot_manager.disconnect_all()
        logger.info("All workers stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workers stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")