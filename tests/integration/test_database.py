import pytest
from sqlalchemy import text

from app.database.database import init_db, drop_db
from app.database.models import *

class TestDatabaseIntegration:
    def test_init_db(self):
        init_db()
        assert True

    def test_drop_db(self):
        drop_db()
        assert True

    def test_tables_exist(self, db_session):
        tables = [
            "users",
            "telegram_accounts",
            "telegram_sources",
            "scan_jobs",
            "whatsapp_links",
            "link_sources",
            "link_analysis_runs",
            "wallet_links",
            "whatsapp_accounts",
            "exports",
            "job_logs"
        ]
        
        for table in tables:
            result = db_session.execute(
                text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            )
            assert result.first() is not None