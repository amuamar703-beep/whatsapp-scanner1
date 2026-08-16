from typing import Dict, Any
from datetime import datetime, timedelta

from app.database.database import get_db
from app.database.repositories import (
    UserRepository,
    ScanJobRepository,
    WhatsAppLinkRepository,
    WalletLinkRepository
)
from app.core.enums import JobStatus, LinkStatus

class StatisticsService:
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            wallet_repo = WalletLinkRepository(db)

            jobs = scan_job_repo.get_by_user_id(user_id)
            
            total_jobs = len(jobs)
            completed_jobs = len([j for j in jobs if j.status == JobStatus.COMPLETED])
            running_jobs = len([j for j in jobs if j.status == JobStatus.RUNNING])
            failed_jobs = len([j for j in jobs if j.status == JobStatus.FAILED])

            total_links = wallet_repo.count_by_user(user_id)
            direct_links = wallet_repo.count_by_user_and_category(user_id, "direct_join")
            request_links = wallet_repo.count_by_user_and_category(user_id, "request_join")

            return {
                "success": True,
                "stats": {
                    "total_jobs": total_jobs,
                    "completed_jobs": completed_jobs,
                    "running_jobs": running_jobs,
                    "failed_jobs": failed_jobs,
                    "wallet_links": total_links,
                    "direct_links": direct_links,
                    "request_links": request_links
                }
            }

    async def get_admin_stats(self) -> Dict[str, Any]:
        async with get_db() as db:
            user_repo = UserRepository(db)
            scan_job_repo = ScanJobRepository(db)
            link_repo = WhatsAppLinkRepository(db)
            wallet_repo = WalletLinkRepository(db)

            total_users = user_repo.count()
            total_jobs = scan_job_repo.count()
            completed_jobs = scan_job_repo.count(status=JobStatus.COMPLETED)
            running_jobs = scan_job_repo.count(status=JobStatus.RUNNING)
            failed_jobs = scan_job_repo.count(status=JobStatus.FAILED)

            total_links = link_repo.count()
            direct_links = link_repo.count(status=LinkStatus.DIRECT_JOIN)
            request_links = link_repo.count(status=LinkStatus.REQUEST_JOIN)
            invalid_links = link_repo.count(status=LinkStatus.INVALID)

            total_wallet = wallet_repo.count()

            return {
                "success": True,
                "stats": {
                    "total_users": total_users,
                    "total_jobs": total_jobs,
                    "completed_jobs": completed_jobs,
                    "running_jobs": running_jobs,
                    "failed_jobs": failed_jobs,
                    "total_links": total_links,
                    "direct_links": direct_links,
                    "request_links": request_links,
                    "invalid_links": invalid_links,
                    "wallet_links": total_wallet
                }
            }

    async def get_job_stats(self, job_id: str) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)

            job = scan_job_repo.get(job_id)
            if not job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            return {
                "success": True,
                "job": {
                    "id": job.id,
                    "type": job.type.value,
                    "status": job.status.value,
                    "progress": job.progress_percent,
                    "total_messages": job.total_messages,
                    "processed_messages": job.processed_messages,
                    "total_urls": job.total_urls,
                    "whatsapp_urls": job.whatsapp_urls,
                    "unique_urls": job.unique_urls,
                    "started_at": job.started_at,
                    "finished_at": job.finished_at,
                    "duration": (job.finished_at - job.started_at).total_seconds() if job.finished_at and job.started_at else None
                }
            }