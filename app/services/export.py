import os
import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from app.database.database import get_db
from app.database.repositories import (
    ExportRepository,
    WalletLinkRepository,
    WhatsAppLinkRepository,
    ScanJobRepository
)
from app.core.enums import ExportFormat, WalletCategory, JobStatus, JobType
from app.workers.queue import QueueManager

class ExportService:
    def __init__(self):
        self.queue_manager = QueueManager()
        self.storage_path = "storage/exports"

    async def start_export(self, user_id: int, format_type: ExportFormat, category: WalletCategory) -> Dict[str, Any]:
        async with get_db() as db:
            scan_job_repo = ScanJobRepository(db)

            job_data = {
                "type": JobType.EXPORT,
                "user_id": user_id,
                "format": format_type.value,
                "category": category.value
            }

            job_id = await self.queue_manager.push(job_data)

            scan_job_repo.create(
                id=job_id,
                user_id=user_id,
                type=JobType.EXPORT,
                status=JobStatus.PENDING
            )

            return {
                "success": True,
                "job_id": str(job_id)
            }

    async def get_export_status(self, job_id: UUID) -> Dict[str, Any]:
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
                "started_at": scan_job.started_at,
                "finished_at": scan_job.finished_at
            }

    async def get_export_file(self, user_id: int, export_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            export_repo = ExportRepository(db)

            export = export_repo.get(export_id)
            if not export:
                return {
                    "success": False,
                    "error": "الملف غير موجود"
                }

            if export.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            if not os.path.exists(export.file_path):
                return {
                    "success": False,
                    "error": "الملف غير موجود على الخادم"
                }

            return {
                "success": True,
                "file_path": export.file_path,
                "file_name": os.path.basename(export.file_path),
                "format": export.format.value,
                "total_links": export.total_links,
                "created_at": export.created_at,
                "expires_at": export.expires_at
            }

    async def list_exports(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            export_repo = ExportRepository(db)

            exports = export_repo.get_by_user_id(user_id)

            result = []
            for exp in exports:
                result.append({
                    "id": exp.id,
                    "format": exp.format.value,
                    "category": exp.category.value if exp.category else None,
                    "total_links": exp.total_links,
                    "file_size": exp.file_size,
                    "created_at": exp.created_at,
                    "expires_at": exp.expires_at
                })

            return {
                "success": True,
                "total": len(result),
                "exports": result
            }

    async def delete_export(self, user_id: int, export_id: UUID) -> Dict[str, Any]:
        async with get_db() as db:
            export_repo = ExportRepository(db)

            export = export_repo.get(export_id)
            if not export:
                return {
                    "success": False,
                    "error": "الملف غير موجود"
                }

            if export.user_id != user_id:
                return {
                    "success": False,
                    "error": "غير مصرح لك"
                }

            if os.path.exists(export.file_path):
                try:
                    os.remove(export.file_path)
                except Exception:
                    pass

            export_repo.delete(export_id)

            return {
                "success": True,
                "message": "تم حذف الملف بنجاح"
            }

    async def generate_export_content(self, user_id: int, category: WalletCategory, format_type: ExportFormat) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)
            link_repo = WhatsAppLinkRepository(db)

            wallet_links = wallet_repo.get_by_user_and_category(user_id, category)

            links_data = []
            for wl in wallet_links:
                link = link_repo.get(wl.link_id)
                if link:
                    links_data.append({
                        "url": link.display_url or link.normalized_url,
                        "status": link.status.value,
                        "source": "wallet",
                        "saved_at": wl.saved_at.isoformat()
                    })

            if not links_data:
                return {
                    "success": False,
                    "error": "لا توجد روابط للتصدير"
                }

            os.makedirs(self.storage_path, exist_ok=True)
            file_name = f"export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type.value}"
            file_path = os.path.join(self.storage_path, file_name)

            if format_type == ExportFormat.TXT:
                content = "\n".join([item["url"] for item in links_data])
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

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

            return {
                "success": True,
                "file_path": file_path,
                "file_name": file_name,
                "total_links": len(links_data)
            }