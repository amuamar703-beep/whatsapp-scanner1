from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.database.database import get_db
from app.database.repositories import (
    ScanJobRepository,
    TelegramSourceRepository,
    TelegramAccountRepository,
    WhatsAppLinkRepository,
    LinkSourceRepository,
    JobLogRepository
)
from app.core.enums import JobStatus, JobType, AccessStatus, LinkStatus
from app.core.constants import MAX_MESSAGES_PER_SCAN
from app.userbot import UserbotManager, SourceResolver, AccessChecker, MessageScanner, URLExtractor, URLNormalizer, Deduplicator
from app.workers.queue import QueueManager

class ExplorationService:
    def __init__(self):
        self.userbot_manager = UserbotManager()
        self.queue_manager = QueueManager()
        self.url_extractor = URLExtractor()
        self.url_normalizer = URLNormalizer()
        self.deduplicator = Deduplicator()

    async def start_exploration(self, user_id: int, source_input: str) -> Dict[str, Any]:
        async with get_db() as db:
            account_repo = TelegramAccountRepository(db)
            source_repo = TelegramSourceRepository(db)
            scan_job_repo = ScanJobRepository(db)
            job_log_repo = JobLogRepository(db)

            account = account_repo.get_primary_by_user_id(user_id)
            if not account:
                return {
                    "success": False,
                    "error": "لا يوجد حساب Telegram مرتبط"
                }

            parsed = SourceResolver.parse_input(source_input)
            if parsed["type"] == "unknown":
                return {
                    "success": False,
                    "error": "لم يتم التعرف على المصدر"
                }

            client = await self.userbot_manager.get_client(account.id, account.session_encrypted)
            entity, info = await SourceResolver.resolve(client, source_input)

            if entity is None or not info:
                return {
                    "success": False,
                    "error": "تعذر الوصول إلى المصدر"
                }

            source, created = source_repo.get_or_create(
                user_id,
                info["id"],
                username=info.get("username"),
                title=info.get("title"),
                type=info.get("type")
            )

            access_result = await AccessChecker.check_access(client, entity, info)
            source_repo.update_access_status(source.id, access_result["access_status"])

            if access_result["access_status"] != AccessStatus.ACCESSIBLE:
                return {
                    "success": False,
                    "error": f"المصدر غير متاح: {access_result['access_status'].value}",
                    "access_status": access_result["access_status"]
                }

            job_data = {
                "type": JobType.SOURCE_SCAN,
                "user_id": user_id,
                "source_id": source.id
            }

            job_id = await self.queue_manager.push(job_data)

            scan_job_repo.create(
                id=job_id,
                user_id=user_id,
                source_id=source.id,
                type=JobType.SOURCE_SCAN,
                status=JobStatus.PENDING
            )

            job_log_repo.create_log(
                job_id,
                "info",
                "exploration_started",
                f"Exploration started for source: {info.get('title') or info.get('username')}"
            )

            return {
                "success": True,
                "job_id": str(job_id),
                "source_id": source.id,
                "source_info": info
            }

    async def get_exploration_status(self, job_id: UUID) -> Dict[str, Any]:
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
                "total_messages": scan_job.total_messages or 0,
                "processed_messages": scan_job.processed_messages or 0,
                "total_urls": scan_job.total_urls or 0,
                "whatsapp_urls": scan_job.whatsapp_urls or 0,
                "unique_urls": scan_job.unique_urls or 0,
                "started_at": scan_job.started_at,
                "finished_at": scan_job.finished_at
            }

    async def get_exploration_results(self, job_id: UUID, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            link_repo = WhatsAppLinkRepository(db)
            link_source_repo = LinkSourceRepository(db)

            scan_job = scan_job_repo.get(job_id)
            if not scan_job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            if scan_job.status != JobStatus.COMPLETED:
                return {
                    "success": False,
                    "error": "المهمة لم تكتمل بعد"
                }

            source_links = link_source_repo.get_by_source_id(scan_job.source_id)
            link_ids = [ls.link_id for ls in source_links]

            total = len(link_ids)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1

            start = (page - 1) * per_page
            end = start + per_page

            paginated_link_ids = link_ids[start:end]

            links = []
            for link_id in paginated_link_ids:
                link = link_repo.get(link_id)
                if link:
                    links.append({
                        "id": link.id,
                        "url": link.display_url or link.normalized_url,
                        "status": link.status.value,
                        "first_seen": link.first_seen
                    })

            return {
                "success": True,
                "total": total,
                "page": page,
                "total_pages": total_pages,
                "links": links,
                "job_id": str(job_id),
                "source_title": scan_job.source.title if scan_job.source else "غير معروف"
            }

    async def cancel_exploration(self, job_id: UUID, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)
            job_log_repo = JobLogRepository(db)

            scan_job = scan_job_repo.get(job_id)
            if not scan_job:
                return {
                    "success": False,
                    "error": "المهمة غير موجودة"
                }

            if scan_job.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك بإلغاء هذه المهمة"
                }

            if scan_job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                return {
                    "success": False,
                    "error": f"لا يمكن إلغاء مهمة بحالة {scan_job.status.value}"
                }

            scan_job_repo.mark_cancelled(job_id)

            job_log_repo.create_log(
                job_id,
                "warning",
                "exploration_cancelled",
                "Exploration cancelled by user"
            )

            return {
                "success": True,
                "message": "تم إلغاء المهمة بنجاح"
            }