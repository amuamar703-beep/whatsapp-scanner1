import asyncio
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.workers.base_worker import BaseWorker
from app.workers.queue import QueueManager
from app.workers.exceptions import AnalysisWorkerError

from app.analyzers import WhatsAppAnalyzer
from app.database.database import get_db
from app.database.repositories import (
    ScanJobRepository,
    WhatsAppLinkRepository,
    LinkAnalysisRunRepository,
    JobLogRepository
)
from app.core.enums import JobStatus, LinkStatus

class AnalysisWorker(BaseWorker):
    def __init__(self, queue_manager: QueueManager):
        super().__init__(queue_manager)
        self.analyzer = WhatsAppAnalyzer()

    async def process_job(self):
        job_data = await self.queue_manager.pop(timeout=5)
        if not job_data:
            return

        job_id = job_data.get("job_id")
        try:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                link_repo = WhatsAppLinkRepository(db)
                analysis_run_repo = LinkAnalysisRunRepository(db)
                job_log_repo = JobLogRepository(db)

                scan_job = scan_job_repo.get(job_id)
                if not scan_job:
                    raise AnalysisWorkerError(f"Job {job_id} not found")

                scan_job_repo.update(job_id, status=JobStatus.RUNNING, started_at=datetime.now())
                job_log_repo.create_log(
                    job_id,
                    "info",
                    "analysis_started",
                    "Starting link analysis"
                )

                pending_links = link_repo.get_pending_analysis(limit=1000)
                analyzed_count = 0
                direct_count = 0
                request_count = 0
                invalid_count = 0
                other_count = 0

                for link in pending_links:
                    try:
                        result = await self.analyzer.analyze(link.normalized_url)
                        
                        analysis_run_repo.create_run(
                            link.id,
                            result.status,
                            confidence=result.confidence.value,
                            response_data=str(result.details)
                        )
                        
                        link_repo.update_status(link.id, result.status, result.confidence.value)
                        link_repo.increment_check_count(link.id)
                        
                        analyzed_count += 1
                        
                        if result.status == LinkStatus.DIRECT_JOIN:
                            direct_count += 1
                        elif result.status == LinkStatus.REQUEST_JOIN:
                            request_count += 1
                        elif result.status == LinkStatus.INVALID:
                            invalid_count += 1
                        else:
                            other_count += 1

                        if analyzed_count % 10 == 0:
                            scan_job_repo.update_progress(
                                job_id,
                                analyzed_count
                            )

                    except Exception as e:
                        job_log_repo.create_log(
                            job_id,
                            "warning",
                            "analysis_error",
                            f"Error analyzing link {link.normalized_url}: {e}"
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
                    "analysis_completed",
                    f"Analysis completed. Analyzed: {analyzed_count}, "
                    f"Direct: {direct_count}, Request: {request_count}, Invalid: {invalid_count}"
                )

        except Exception as e:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                job_log_repo = JobLogRepository(db)
                
                scan_job_repo.mark_failed(job_id, "error", str(e))
                job_log_repo.create_log(
                    job_id,
                    "error",
                    "analysis_failed",
                    str(e)
                )

    async def stop(self):
        await self.analyzer.close()
        await super().stop()

    async def handle_error(self, error: Exception):
        if isinstance(error, asyncio.CancelledError):
            pass