import pytest
from datetime import datetime
from uuid import UUID

from app.database.models import (
    User,
    TelegramAccount,
    TelegramSource,
    ScanJob,
    WhatsAppLink,
    LinkSource,
    LinkAnalysisRun,
    WalletLink,
    WhatsAppAccount,
    Export,
    JobLog
)
from app.core.enums import (
    UserStatus,
    TelegramAccountStatus,
    SourceType,
    AccessStatus,
    JobType,
    JobStatus,
    LinkStatus,
    ConfidenceLevel,
    WalletCategory,
    ExportFormat,
    NotificationLevel
)

class TestUser:
    def test_create_user(self, db_session):
        user = User(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.status == UserStatus.ACTIVE

    def test_user_relationships(self, db_session, sample_user):
        assert sample_user.telegram_accounts == []
        assert sample_user.telegram_sources == []
        assert sample_user.scan_jobs == []
        assert sample_user.wallet_links == []

class TestTelegramAccount:
    def test_create_telegram_account(self, db_session, sample_user):
        account = TelegramAccount(
            user_id=sample_user.id,
            telegram_user_id=987654321,
            phone_masked="+9665****1234",
            session_encrypted="encrypted_data",
            status=TelegramAccountStatus.ACTIVE,
            is_primary=True
        )
        db_session.add(account)
        db_session.commit()
        
        assert account.id is not None
        assert account.user_id == sample_user.id
        assert account.telegram_user_id == 987654321
        assert account.phone_masked == "+9665****1234"
        assert account.status == TelegramAccountStatus.ACTIVE
        assert account.is_primary is True

class TestTelegramSource:
    def test_create_telegram_source(self, db_session, sample_user):
        source = TelegramSource(
            owner_user_id=sample_user.id,
            telegram_chat_id=-100123456789,
            username="test_group",
            title="Test Group",
            type=SourceType.SUPERGROUP,
            access_status=AccessStatus.ACCESSIBLE,
            can_read_messages=True
        )
        db_session.add(source)
        db_session.commit()
        
        assert source.id is not None
        assert source.owner_user_id == sample_user.id
        assert source.telegram_chat_id == -100123456789
        assert source.username == "test_group"
        assert source.title == "Test Group"
        assert source.type == SourceType.SUPERGROUP
        assert source.access_status == AccessStatus.ACCESSIBLE
        assert source.can_read_messages is True

class TestWhatsAppLink:
    def test_create_whatsapp_link(self, db_session):
        link = WhatsAppLink(
            normalized_url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            display_url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            status=LinkStatus.DISCOVERED,
            confidence=ConfidenceLevel.LOW,
            check_count=0
        )
        db_session.add(link)
        db_session.commit()
        
        assert link.id is not None
        assert link.normalized_url == "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        assert link.status == LinkStatus.DISCOVERED
        assert link.confidence == ConfidenceLevel.LOW
        assert link.check_count == 0

    def test_whatsapp_link_unique_constraint(self, db_session, sample_whatsapp_link):
        link2 = WhatsAppLink(
            normalized_url=sample_whatsapp_link.normalized_url,
            display_url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        db_session.add(link2)
        with pytest.raises(Exception):
            db_session.commit()

class TestWalletLink:
    def test_create_wallet_link(self, db_session, sample_user, sample_whatsapp_link):
        wallet_link = WalletLink(
            user_id=sample_user.id,
            link_id=sample_whatsapp_link.id,
            category=WalletCategory.DIRECT_JOIN
        )
        db_session.add(wallet_link)
        db_session.commit()
        
        assert wallet_link.id is not None
        assert wallet_link.user_id == sample_user.id
        assert wallet_link.link_id == sample_whatsapp_link.id
        assert wallet_link.category == WalletCategory.DIRECT_JOIN

    def test_wallet_link_unique_constraint(self, db_session, sample_user, sample_whatsapp_link, sample_wallet_link):
        wallet_link2 = WalletLink(
            user_id=sample_user.id,
            link_id=sample_whatsapp_link.id,
            category=WalletCategory.REQUEST_JOIN
        )
        db_session.add(wallet_link2)
        with pytest.raises(Exception):
            db_session.commit()