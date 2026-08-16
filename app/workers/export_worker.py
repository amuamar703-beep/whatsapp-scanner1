import os
import json
import csv
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.workers.base_worker import BaseWorker
from app.workers.queue import QueueManager
from app.workers.exceptions import ExportWorkerError

from app.database.database import get_db
from app.database.repositories import (
    ScanJobRepository,
    ExportRepository,
    WalletLinkRepository,
    WhatsAppLinkRepository,
    JobLogRepository
)
from app.core.enums import JobStatus, ExportFormat, WalletCategory
from app.core.config import settings

class ExportWorker(BaseWorker):
    def __init__(self, queue_manager: QueueManager):
        super().__init__(queue_manager)
        self.storage_path = "storage/exports"

    async def process_job(self):
        job_data = await self.queue_manager.pop(timeout=5)
        if not job_data:
            return

        job_id = job_data.get("job_id")
        try:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                export_repo = ExportRepository(db)
                wallet_repo = WalletLinkRepository(db)
                link_repo = WhatsAppLinkRepository(db)
                job_log_repo = JobLogRepository(db)

                scan_job = scan_job_repo.get(job_id)
                if not scan_job:
                    raise ExportWorkerError(f"Job {job_id} not found")

                format_type = job_data.get("format", ExportFormat.TXT)
                category = job_data.get("category")

                wallet_links = wallet_repo.get_by_user_and_category(
                    scan_job.user_id,
                    category
                )

                if not wallet_links:
                    raise ExportWorkerError("No links found in wallet for export")

                links_data = []
                for wallet_link in wallet_links:
                    link = link_repo.get(wallet_link.link_id)
                    if link:
                        links_data.append({
                            "url": link.display_url or link.normalized_url,
                            "status": link.status.value,
                            "source": "wallet",
                            "saved_at": wallet_link.saved_at.isoformat()
                        })

                if not links_data:
                    raise ExportWorkerError("No valid links to export")

                os.makedirs(self.storage_path, exist_ok=True)
                file_name = f"export_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type.value}"
                file_path = os.path.join(self.storage_path, file_name)

                if format_type == ExportFormat.TXT:
                    file_content = "\n".join([item["url"] for item in links_data])
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(file_content)

                elif format_type == ExportFormat.CSV:
                    with open(file_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=["url", "status", "source", "saved_at"])
                        writer.writeheader()
                        writer.writerows(links_data)

                elif format_type == ExportFormat.JSON:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "status": "success",
                            "total": len(links_data),
                            "links": links_data
                        }, f, ensure_ascii=False, indent=2)

                export_repo.create_export(
                    scan_job.user_id,
                    format_type,
                    file_path,
                    category=category.value if category else None,
                    total_links=len(links_data),
                    file_size=os.path.getsize(file_path),
                    expires_at=datetime.now()
                )

                scan_job_repo.update(
                    job_id,
                    status=JobStatus.COMPLETED,
                    finished_at=datetime.now()
                )

                job_log_repo.create_log(
                    job_id,
                    "success",
                    "export_completed",
                    f"Export completed. Format: {format_type.value}, Links: {len(links_data)}"
                )

        except Exception as e:
            async with get_db() as db:
                scan_job_repo = ScanJobRepository(db)
                job_log_repo = JobLogRepository(db)
                
                scan_job_repo.mark_failed(job_id, "error", str(e))
                job_log_repo.create_log(
                    job_id,
                    "error",
                    "export_failed",
                    str(e)
                )

    async def handle_error(self, error: Exception):
        if isinstance(error, asyncio.CancelledError):
            pass