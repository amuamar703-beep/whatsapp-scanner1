import asyncio
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.workers.base_worker import BaseWorker
from app.workers.queue import QueueManager
from app.workers.exceptions import RescanWorkerError

from app.analyzers import WhatsAppAnalyzer
from app.database.database import get_db
from app.database.repositories import (
    ScanJobRepository,
    WhatsAppLinkRepository,
    LinkAnalysisRunRepository,
    JobLogRepository
)
from app.core.enums import JobStatus, LinkStatus

class RescanWorker(BaseWorker):
    def __init__(self, queue_manager: QueueManager):
        super().__init__(queue_manager)
        self.analyzer = WhatsAppAnalyzer()

    async def process_job(self):
        job_data = await self.queue_manager.pop(timeout=5)
        if not job_data:
            return

        job_id = job_data.get("job_id")
        link_ids = job_data.get("link_ids", [])

        try:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                link_repo = WhatsAppLinkRepository(db)
                analysis_run_repo = LinkAnalysisRunRepository(db)
                job_log_repo = JobLogRepository(db)

                scan_job = scan_job_repo.get(job_id)
                if not scan_job:
                    raise RescanWorkerError(f"Job {job_id} not found")

                scan_job_repo.update(job_id, status=JobStatus.RUNNING, started_at=datetime.now())
                job_log_repo.create_log(
                    job_id,
                    "info",
                    "rescan_started",
                    f"Starting rescan for {len(link_ids)} links"
                )

                analyzed_count = 0
                status_changes = 0

                for link_id in link_ids:
                    link = link_repo.get(link_id)
                    if not link:
                        continue

                    try:
                        result = await self.analyzer.analyze(link.normalized_url)
                        
                        old_status = link.status
                        
                        analysis_run_repo.create_run(
                            link.id,
                            result.status,
                            confidence=result.confidence.value,
                            response_data=str(result.details)
                        )
                        
                        link_repo.update_status(link.id, result.status, result.confidence.value)
                        link_repo.increment_check_count(link.id)
                        
                        analyzed_count += 1
                        
                        if old_status != result.status:
                            status_changes += 1

                        if analyzed_count % 10 == 0:
                            scan_job_repo.update_progress(
                                job_id,
                                analyzed_count
                            )

                    except Exception as e:
                        job_log_repo.create_log(
                            job_id,
                            "warning",
                            "rescan_error",
                            f"Error rescanning link {link.normalized_url}: {e}"
                        )

                scan_job_repo.update(
                    job_id,
                    status=JobStatus.COMPLETED,
                    finished_at=datetime.now(),
                    processed_messages=analyzed_count,
                    progress_percent=100
                )

                job_log_repo.create_log(
                    job_id,
                    "success",
                    "rescan_completed",
                    f"Rescan completed. Analyzed: {analyzed_count}, Status changes: {status_changes}"
                )

        except Exception as e:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                job_log_repo = JobLogRepository(db)
                
                scan_job_repo.mark_failed(job_id, "error", str(e))
                job_log_repo.create_log(
                    job_id,
                    "error",
                    "rescan_failed",
                    str(e)
                )

    async def stop(self):
        await self.analyzer.close()
        await super().stop()

    async def handle_error(self, error: Exception):
        if isinstance(error, asyncio.CancelledError):
            pass