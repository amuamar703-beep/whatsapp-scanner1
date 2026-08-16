import pytest
from uuid import UUID

from app.database.repositories import (
    UserRepository,
    TelegramAccountRepository,
    TelegramSourceRepository,
    ScanJobRepository,
    WhatsAppLinkRepository,
    LinkSourceRepository,
    LinkAnalysisRunRepository,
    WalletLinkRepository,
    WhatsAppAccountRepository,
    ExportRepository,
    JobLogRepository
)
from app.core.enums import (
    UserStatus,
    TelegramAccountStatus,
    JobType,
    JobStatus,
    LinkStatus,
    ConfidenceLevel,
    WalletCategory,
    ExportFormat,
    NotificationLevel
)

class TestUserRepository:
    def test_get_or_create(self, db_session):
        repo = UserRepository(db_session)
        user, created = repo.get_or_create(123456789, username="test")
        assert user is not None
        assert created is True
        assert user.telegram_id == 123456789
        
        user2, created2 = repo.get_or_create(123456789)
        assert user2.id == user.id
        assert created2 is False

    def test_get_by_telegram_id(self, db_session, sample_user):
        repo = UserRepository(db_session)
        user = repo.get_by_telegram_id(sample_user.telegram_id)
        assert user is not None
        assert user.id == sample_user.id

class TestTelegramAccountRepository:
    def test_get_primary_by_user_id(self, db_session, sample_user, sample_telegram_account):
        repo = TelegramAccountRepository(db_session)
        account = repo.get_primary_by_user_id(sample_user.id)
        assert account is not None
        assert account.id == sample_telegram_account.id
        assert account.is_primary is True

    def test_set_primary(self, db_session, sample_user):
        repo = TelegramAccountRepository(db_session)
        account1 = repo.create(
            user_id=sample_user.id,
            telegram_user_id=111111,
            phone_masked="+9665****1111",
            session_encrypted="encrypted_1",
            is_primary=True
        )
        account2 = repo.create(
            user_id=sample_user.id,
            telegram_user_id=222222,
            phone_masked="+9665****2222",
            session_encrypted="encrypted_2",
            is_primary=False
        )
        db_session.commit()
        
        repo.set_primary(account2.id, sample_user.id)
        db_session.commit()
        
        account1_refresh = repo.get(account1.id)
        account2_refresh = repo.get(account2.id)
        assert account1_refresh.is_primary is False
        assert account2_refresh.is_primary is True

class TestWhatsAppLinkRepository:
    def test_get_or_create(self, db_session):
        repo = WhatsAppLinkRepository(db_session)
        url = "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        link, created = repo.get_or_create(url)
        assert link is not None
        assert created is True
        assert link.normalized_url == url
        
        link2, created2 = repo.get_or_create(url)
        assert link2.id == link.id
        assert created2 is False

    def test_get_by_normalized_url(self, db_session, sample_whatsapp_link):
        repo = WhatsAppLinkRepository(db_session)
        link = repo.get_by_normalized_url(sample_whatsapp_link.normalized_url)
        assert link is not None
        assert link.id == sample_whatsapp_link.id

    def test_update_status(self, db_session, sample_whatsapp_link):
        repo = WhatsAppLinkRepository(db_session)
        link = repo.update_status(
            sample_whatsapp_link.id,
            LinkStatus.DIRECT_JOIN,
            ConfidenceLevel.HIGH.value
        )
        assert link.status == LinkStatus.DIRECT_JOIN
        assert link.confidence == ConfidenceLevel.HIGH

class TestWalletLinkRepository:
    def test_get_or_create(self, db_session, sample_user, sample_whatsapp_link):
        repo = WalletLinkRepository(db_session)
        wallet_link, created = repo.get_or_create(
            sample_user.id,
            sample_whatsapp_link.id,
            WalletCategory.DIRECT_JOIN
        )
        assert wallet_link is not None
        assert created is True
        assert wallet_link.user_id == sample_user.id
        assert wallet_link.link_id == sample_whatsapp_link.id
        
        wallet_link2, created2 = repo.get_or_create(
            sample_user.id,
            sample_whatsapp_link.id,
            WalletCategory.REQUEST_JOIN
        )
        assert wallet_link2.id == wallet_link.id
        assert created2 is False

    def test_count_by_user(self, db_session, sample_user, sample_whatsapp_link, sample_wallet_link):
        repo = WalletLinkRepository(db_session)
        count = repo.count_by_user(sample_user.id)
        assert count >= 1