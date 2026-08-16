from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from app.database.database import get_db
from app.database.repositories import (
    ScanJobRepository,
    WhatsAppLinkRepository,
    LinkAnalysisRunRepository,
    JobLogRepository
)
from app.core.enums import JobStatus, JobType, LinkStatus
from app.analyzers import WhatsAppAnalyzer
from app.workers.queue import QueueManager

class AnalysisService:
    def __init__(self):
        self.analyzer = WhatsAppAnalyzer()
        self.queue_manager = QueueManager()

    async def start_analysis(self, user_id: int, source_job_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            job_log_repo = JobLogRepository(db)

            source_job = scan_job_repo.get(source_job_id)
            if not source_job:
                return {
                    "success": False,
                    "error": "المهمة المصدر غير موجودة"
                }

            if source_job.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            if source_job.status != JobStatus.COMPLETED:
                return {
                    "success": False,
                    "error": "لم تكتمل عملية الاستكشاف بعد"
                }

            job_data = {
                "type": JobType.LINK_ANALYSIS,
                "user_id": user_id,
                "source_id": source_job.source_id
            }

            job_id = await self.queue_manager.push(job_data)

            scan_job_repo.create(
                id=job_id,
                user_id=user_id,
                source_id=source_job.source_id,
                type=JobType.LINK_ANALYSIS,
                status=JobStatus.PENDING
            )

            job_log_repo.create_log(
                job_id,
                "info",
                "analysis_started",
                "Link analysis started"
            )

            return {
                "success": True,
                "job_id": str(job_id)
            }

    async def get_analysis_status(self, job_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            scan_job = scan_job_repo.get(job_id)

            if not scan_job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            return {
                "success": True,
                "status": scan_job.status.value,
                "progress": scan_job.progress_percent or 0,
                "processed": scan_job.processed_messages or 0,
                "started_at": scan_job.started_at,
                "finished_at": scan_job.finished_at
            }

    async def get_analysis_results(self, job_id: UUID, category: Optional[str] = None) -> Dict[str, Any]:
        async with get_db() as db:
            link_repo = WhatsAppLinkRepository(db)

            if category:
                try:
                    status = LinkStatus(category)
                    links = link_repo.get_by_status(status)
                except ValueError:
                    return {
                        "success": False,
                        "error": "فئة غير صالحة"
                    }
            else:
                links = link_repo.get_by_status(LinkStatus.DISCOVERED)

            results = {
                "total": len(links),
                "direct_join": 0,
                "request_join": 0,
                "invalid": 0,
                "revoked_or_changed": 0,
                "temporary_error": 0,
                "unknown": 0,
                "links": []
            }

            for link in links:
                if link.status == LinkStatus.DIRECT_JOIN:
                    results["direct_join"] += 1
                elif link.status == LinkStatus.REQUEST_JOIN:
                    results["request_join"] += 1
                elif link.status == LinkStatus.INVALID:
                    results["invalid"] += 1
                elif link.status == LinkStatus.REVOKED_OR_CHANGED:
                    results["revoked_or_changed"] += 1
                elif link.status == LinkStatus.TEMPORARY_ERROR:
                    results["temporary_error"] += 1
                else:
                    results["unknown"] += 1

                if not category or link.status.value == category:
                    results["links"].append({
                        "id": link.id,
                        "url": link.display_url or link.normalized_url,
                        "status": link.status.value,
                        "confidence": link.confidence.value if link.confidence else "low",
                        "last_checked": link.last_checked
                    })

            return {
                "success": True,
                "results": results
            }

    async def rescan_links(self, user_id: int, link_ids: List[int]) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            job_log_repo = JobLogRepository(db)

            job_data = {
                "type": JobType.RESCAN,
                "user_id": user_id,
                "link_ids": link_ids
            }

            job_id = await self.queue_manager.push(job_data)

            scan_job_repo.create(
                id=job_id,
                user_id=user_id,
                type=JobType.RESCAN,
                status=JobStatus.PENDING
            )

            job_log_repo.create_log(
                job_id,
                "info",
                "rescan_started",
                f"Rescan started for {len(link_ids)} links"
            )

            return {
                "success": True,
                "job_id": str(job_id)
            }

    async def analyze_single_link(self, link_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            link_repo = WhatsAppLinkRepository(db)
            analysis_run_repo = LinkAnalysisRunRepository(db)

            link = link_repo.get(link_id)
            if not link:
                return {
                    "success": False,
                    "error": "الرابط غير موجود"
                }

            result = await self.analyzer.analyze(link.normalized_url)

            analysis_run_repo.create_run(
                link.id,
                result.status,
                confidence=result.confidence.value,
                response_data=str(result.details)
            )

            link_repo.update_status(link.id, result.status, result.confidence.value)
            link_repo.increment_check_count(link.id)

            return {
                "success": True,
                "url": link.display_url or link.normalized_url,
                "status": result.status.value,
                "confidence": result.confidence.value,
                "details": result.details
            }