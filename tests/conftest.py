import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.database.models import *
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(db_session: Session):
    from app.database.repositories import UserRepository
    repo = UserRepository(db_session)
    user, created = repo.get_or_create(
        123456789,
        username="test_user",
        first_name="Test",
        language="ar"
    )
    db_session.commit()
    return user

@pytest.fixture
def sample_telegram_account(db_session: Session, sample_user):
    from app.database.repositories import TelegramAccountRepository
    repo = TelegramAccountRepository(db_session)
    account = repo.create(
        user_id=sample_user.id,
        telegram_user_id=987654321,
        phone_masked="+9665****1234",
        session_encrypted="encrypted_session_data",
        is_primary=True
    )
    db_session.commit()
    return account

@pytest.fixture
def sample_telegram_source(db_session: Session, sample_user):
    from app.database.repositories import TelegramSourceRepository
    repo = TelegramSourceRepository(db_session)
    source, created = repo.get_or_create(
        sample_user.id,
        -100123456789,
        username="test_group",
        title="Test Group",
        type="supergroup"
    )
    db_session.commit()
    return source

@pytest.fixture
def sample_whatsapp_link(db_session: Session):
    from app.database.repositories import WhatsAppLinkRepository
    repo = WhatsAppLinkRepository(db_session)
    link, created = repo.get_or_create(
        "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        display_url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    db_session.commit()
    return link

@pytest.fixture
def sample_wallet_link(db_session: Session, sample_user, sample_whatsapp_link):
    from app.database.repositories import WalletLinkRepository
    repo = WalletLinkRepository(db_session)
    wallet_link, created = repo.get_or_create(
        sample_user.id,
        sample_whatsapp_link.id,
        "direct_join"
    )
    db_session.commit()
    return wallet_link