import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.workers.base_worker import BaseWorker
from app.workers.queue import QueueManager
from app.workers.exceptions import ScanWorkerError, FloodWaitError

from app.userbot import (
    UserbotManager,
    SourceResolver,
    AccessChecker,
    MessageScanner,
    URLExtractor,
    URLNormalizer,
    Deduplicator
)
from app.database.database import get_db
from app.database.repositories import (
    ScanJobRepository,
    TelegramSourceRepository,
    TelegramAccountRepository,
    WhatsAppLinkRepository,
    LinkSourceRepository,
    JobLogRepository
)
from app.core.enums import AccessStatus, JobStatus, LinkStatus
from app.core.constants import MAX_MESSAGES_PER_SCAN

class ScanWorker(BaseWorker):
    def __init__(self, queue_manager: QueueManager, userbot_manager: UserbotManager):
        super().__init__(queue_manager)
        self.userbot_manager = userbot_manager
        self.url_extractor = URLExtractor()
        self.url_normalizer = URLNormalizer()
        self.deduplicator = Deduplicator()

    async def process_job(self):
        job_data = await self.queue_manager.pop(timeout=5)
        if not job_data:
            return

        job_id = job_data.get("job_id")
        try:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                source_repo = TelegramSourceRepository(db)
                account_repo = TelegramAccountRepository(db)
                link_repo = WhatsAppLinkRepository(db)
                link_source_repo = LinkSourceRepository(db)
                job_log_repo = JobLogRepository(db)

                scan_job = scan_job_repo.get(job_id)
                if not scan_job:
                    raise ScanWorkerError(f"Job {job_id} not found")

                source = source_repo.get(scan_job.source_id)
                if not source:
                    raise ScanWorkerError(f"Source not found for job {job_id}")

                account = account_repo.get_primary_by_user_id(scan_job.user_id)
                if not account:
                    raise ScanWorkerError(f"No primary Telegram account found for user {scan_job.user_id}")

                scan_job_repo.update(job_id, status=JobStatus.RUNNING, started_at=datetime.now())
                job_log_repo.create_log(
                    job_id,
                    "info",
                    "scan_started",
                    f"Starting scan for source: {source.title or source.username}"
                )

                client = await self.userbot_manager.get_client(account.id, account.session_encrypted)
                if not client:
                    raise ScanWorkerError("Failed to get Telegram client")

                entity = await client.get_entity(source.telegram_chat_id)
                if not entity:
                    raise ScanWorkerError("Failed to resolve entity")

                scanner = MessageScanner(client, entity, limit=MAX_MESSAGES_PER_SCAN)
                messages_processed = 0
                total_urls = 0
                whatsapp_urls = 0
                unique_urls = 0

                async for message in scanner.scan_messages():
                    urls = self.url_extractor.extract_from_message(message)
                    
                    if urls:
                        total_urls += len(urls)
                        
                        whatsapp_urls_list = self.url_extractor.extract_whatsapp_urls(urls)
                        whatsapp_urls += len(whatsapp_urls_list)
                        
                        for url in whatsapp_urls_list:
                            normalized_url = self.url_normalizer.normalize_whatsapp(url)
                            if not normalized_url:
                                continue
                            
                            link, created = link_repo.get_or_create(
                                normalized_url,
                                display_url=url,
                                status=LinkStatus.DISCOVERED
                            )
                            
                            if created:
                                unique_urls += 1
                            
                            link_source, _ = link_source_repo.get_or_create(
                                link.id,
                                source.id,
                                message_id=message.id
                            )
                            link_source_repo.update_last_seen(link_source.id)

                    messages_processed += 1

                    if messages_processed % 100 == 0:
                        scan_job_repo.update_progress(
                            job_id,
                            messages_processed,
                            total_urls,
                            whatsapp_urls
                        )

                scan_job_repo.update(
                    job_id,
                    status=JobStatus.COMPLETED,
                    finished_at=datetime.now(),
                    total_messages=messages_processed,
                    total_urls=total_urls,
                    whatsapp_urls=whatsapp_urls,
                    unique_urls=unique_urls,
                    progress_percent=100
                )

                job_log_repo.create_log(
                    job_id,
                    "success",
                    "scan_completed",
                    f"Scan completed. Messages: {messages_processed}, URLs: {total_urls}, WhatsApp: {whatsapp_urls}"
                )

                source_repo.update_last_scanned(source.id)

        except FloodWaitError as e:
            async with get_db() as db:
                job_log_repo = JobLogRepository(db)
                job_log_repo.create_log(
                    job_id,
                    "warning",
                    "flood_wait",
                    f"Flood wait required: {e.wait_seconds} seconds"
                )
            await asyncio.sleep(e.wait_seconds)
            await self.queue_manager.push(job_data)

        except Exception as e:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                job_log_repo = JobLogRepository(db)
                
                scan_job_repo.mark_failed(job_id, "error", str(e))
                job_log_repo.create_log(
                    job_id,
                    "error",
                    "scan_failed",
                    str(e)
                )

    async def handle_error(self, error: Exception):
        if isinstance(error, asyncio.CancelledError):
            pass