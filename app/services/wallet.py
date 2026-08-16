from typing import Dict, Any, List, Optional
from uuid import UUID

from app.database.database import get_db
from app.database.repositories import (
    WalletLinkRepository,
    WhatsAppLinkRepository,
    ScanJobRepository
)
from app.core.enums import WalletCategory, LinkStatus

class WalletService:
    async def add_to_wallet(self, user_id: int, link_ids: List[int], category: WalletCategory) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)
            link_repo = WhatsAppLinkRepository(db)

            added = 0
            skipped = 0

            for link_id in link_ids:
                link = link_repo.get(link_id)
                if not link:
                    skipped += 1
                    continue

                existing = wallet_repo.get_by_user_and_link(user_id, link_id)
                if existing:
                    skipped += 1
                    continue

                wallet_repo.create(
                    user_id=user_id,
                    link_id=link_id,
                    category=category
                )
                added += 1

            return {
                "success": True,
                "added": added,
                "skipped": skipped,
                "total": len(link_ids)
            }

    async def get_wallet_links(
        self,
        user_id: int,
        category: Optional[WalletCategory] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)
            link_repo = WhatsAppLinkRepository(db)

            if category:
                wallet_links = wallet_repo.get_by_user_and_category(user_id, category)
            else:
                wallet_links = wallet_repo.get_by_user_id(user_id)

            total = len(wallet_links)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1

            start = (page - 1) * per_page
            end = start + per_page

            paginated = wallet_links[start:end]

            links = []
            for wl in paginated:
                link = link_repo.get(wl.link_id)
                if link:
                    links.append({
                        "wallet_id": wl.id,
                        "link_id": link.id,
                        "url": link.display_url or link.normalized_url,
                        "status": link.status.value,
                        "category": wl.category.value,
                        "saved_at": wl.saved_at
                    })

            return {
                "success": True,
                "total": total,
                "page": page,
                "total_pages": total_pages,
                "links": links
            }

    async def get_wallet_stats(self, user_id: int) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)

            total = wallet_repo.count_by_user(user_id)
            direct = wallet_repo.count_by_user_and_category(user_id, WalletCategory.DIRECT_JOIN)
            request = wallet_repo.count_by_user_and_category(user_id, WalletCategory.REQUEST_JOIN)

            return {
                "success": True,
                "total": total,
                "direct_join": direct,
                "request_join": request
            }

    async def remove_from_wallet(self, user_id: int, wallet_ids: List[int]) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)

            deleted = 0
            not_found = 0

            for wallet_id in wallet_ids:
                wallet_link = wallet_repo.get(wallet_id)
                if not wallet_link:
                    not_found += 1
                    continue

                if wallet_link.user_id != user_id:
                    not_found += 1
                    continue

                wallet_repo.delete(wallet_id)
                deleted += 1

            return {
                "success": True,
                "deleted": deleted,
                "not_found": not_found
            }

    async def remove_from_wallet_by_link(self, user_id: int, link_ids: List[int]) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)

            deleted = 0
            not_found = 0

            for link_id in link_ids:
                wallet_link = wallet_repo.get_by_user_and_link(user_id, link_id)
                if not wallet_link:
                    not_found += 1
                    continue

                wallet_repo.delete(wallet_link.id)
                deleted += 1

            return {
                "success": True,
                "deleted": deleted,
                "not_found": not_found
            }

    async def search_wallet(self, user_id: int, query: str) -> Dict[str, Any]:
        async with get_db() as db:
            wallet_repo = WalletLinkRepository(db)
            link_repo = WhatsAppLinkRepository(db)

            wallet_links = wallet_repo.get_by_user_id(user_id)

            results = []
            for wl in wallet_links:
                link = link_repo.get(wl.link_id)
                if link and (query.lower() in (link.display_url or link.normalized_url).lower()):
                    results.append({
                        "wallet_id": wl.id,
                        "link_id": link.id,
                        "url": link.display_url or link.normalized_url,
                        "status": link.status.value,
                        "category": wl.category.value
                    })

            return {
                "success": True,
                "total": len(results),
                "results": results
            }