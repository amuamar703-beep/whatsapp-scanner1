import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services import (
    WalletService,
    ExportService,
    AccountsService,
    SourceService,
    StatisticsService,
    JobsService
)
from app.core.enums import WalletCategory, ExportFormat

class TestWalletService:
    @pytest.mark.asyncio
    async def test_add_to_wallet(self, db_session, sample_user, sample_whatsapp_link):
        service = WalletService()
        result = await service.add_to_wallet(
            sample_user.id,
            [sample_whatsapp_link.id],
            WalletCategory.DIRECT_JOIN
        )
        assert result["success"] is True
        assert result["added"] == 1
        assert result["skipped"] == 0

    @pytest.mark.asyncio
    async def test_get_wallet_links(self, db_session, sample_user, sample_wallet_link):
        service = WalletService()
        result = await service.get_wallet_links(
            sample_user.id,
            WalletCategory.DIRECT_JOIN
        )
        assert result["success"] is True
        assert result["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_wallet_stats(self, db_session, sample_user, sample_wallet_link):
        service = WalletService()
        result = await service.get_wallet_stats(sample_user.id)
        assert result["success"] is True
        assert result["stats"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_remove_from_wallet(self, db_session, sample_user, sample_wallet_link):
        service = WalletService()
        result = await service.remove_from_wallet(
            sample_user.id,
            [sample_wallet_link.id]
        )
        assert result["success"] is True
        assert result["deleted"] == 1

class TestAccountsService:
    @pytest.mark.asyncio
    async def test_add_telegram_account(self, db_session, sample_user):
        service = AccountsService()
        result = await service.add_telegram_account(
            sample_user.id,
            "+966512345678",
            "session_string_test",
            987654321
        )
        assert result["success"] is True
        assert result["account_id"] is not None

    @pytest.mark.asyncio
    async def test_get_telegram_accounts(self, db_session, sample_user, sample_telegram_account):
        service = AccountsService()
        result = await service.get_telegram_accounts(sample_user.id)
        assert result["success"] is True
        assert result["total"] >= 1

    @pytest.mark.asyncio
    async def test_add_whatsapp_account(self, db_session, sample_user):
        service = AccountsService()
        result = await service.add_whatsapp_account(
            sample_user.id,
            "Test Account",
            "+966512345678",
            "https://wa.me/966512345678"
        )
        assert result["success"] is True
        assert result["account_id"] is not None

class TestStatisticsService:
    @pytest.mark.asyncio
    async def test_get_user_stats(self, db_session, sample_user, sample_wallet_link):
        service = StatisticsService()
        result = await service.get_user_stats(sample_user.id)
        assert result["success"] is True
        assert "stats" in result

    @pytest.mark.asyncio
    async def test_get_admin_stats(self, db_session):
        service = StatisticsService()
        result = await service.get_admin_stats()
        assert result["success"] is True
        assert "stats" in result