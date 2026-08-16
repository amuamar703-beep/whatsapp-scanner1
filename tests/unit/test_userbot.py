import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.userbot import (
    UserbotManager,
    SessionManager,
    SourceResolver,
    AccessChecker,
    URLExtractor,
    URLNormalizer,
    Deduplicator
)
from app.core.enums import AccessStatus

class TestSessionManager:
    def test_encrypt_decrypt(self):
        manager = SessionManager()
        data = {
            "session_string": "test_session",
            "phone": "+1234567890",
            "user_id": 123456
        }
        encrypted = manager.pack_session(
            session_string=data["session_string"],
            phone=data["phone"],
            user_id=data["user_id"]
        )
        assert encrypted is not None
        assert len(encrypted) > 0
        
        decrypted = manager.get_session_data(encrypted)
        assert decrypted["session_string"] == data["session_string"]
        assert decrypted["phone"] == data["phone"]
        assert decrypted["user_id"] == data["user_id"]

class TestSourceResolver:
    def test_parse_input(self):
        test_cases = [
            ("@testgroup", "username", "testgroup"),
            ("testgroup", "username", "testgroup"),
            ("https://t.me/testgroup", "username", "testgroup"),
            ("https://t.me/+abcdef12345", "invite_hash", "abcdef12345"),
            ("https://t.me/joinchat/abcdef12345", "invite_hash", "abcdef12345"),
            ("-100123456789", "id", -100123456789),
            ("123456789", "id", 123456789),
            ("invalid input", "unknown", "invalid input")
        ]
        
        for input_text, expected_type, expected_value in test_cases:
            result = SourceResolver.parse_input(input_text)
            assert result["type"] == expected_type
            if expected_type != "unknown":
                assert result["value"] == expected_value

class TestURLExtractor:
    def test_extract_from_text(self):
        extractor = URLExtractor()
        text = """
        Check these links:
        https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ
        https://t.me/testgroup
        https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ?text=test
        https://youtube.com/watch?v=123
        """
        urls = extractor.extract_from_text(text)
        assert len(urls) >= 3
        assert "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ" in urls

    def test_extract_whatsapp_urls(self):
        extractor = URLExtractor()
        urls = [
            "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "https://t.me/testgroup",
            "https://wa.me/+1234567890",
            "https://youtube.com/watch?v=123"
        ]
        whatsapp = extractor.extract_whatsapp_urls(urls)
        assert len(whatsapp) == 2
        assert "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ" in whatsapp
        assert "https://wa.me/+1234567890" in whatsapp

    def test_detect_whatsapp_url(self):
        extractor = URLExtractor()
        assert extractor.detect_whatsapp_url("https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ") is True
        assert extractor.detect_whatsapp_url("https://t.me/testgroup") is False
        assert extractor.detect_whatsapp_url("https://wa.me/+1234567890") is True

    def test_extract_invite_hash(self):
        extractor = URLExtractor()
        hash_value = extractor.extract_invite_hash("https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert hash_value == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        hash_value2 = extractor.extract_invite_hash("https://t.me/testgroup")
        assert hash_value2 is None

class TestURLNormalizer:
    def test_normalize(self):
        normalizer = URLNormalizer()
        test_cases = [
            ("https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ", "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            ("http://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ", "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            ("chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ", "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        ]
        for input_url, expected in test_cases:
            result = normalizer.normalize(input_url)
            assert result == expected

    def test_normalize_whatsapp(self):
        normalizer = URLNormalizer()
        url = "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ?text=test"
        result = normalizer.normalize_whatsapp(url)
        assert result == "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_is_valid_whatsapp_format(self):
        normalizer = URLNormalizer()
        assert normalizer.is_valid_whatsapp_format("https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ") is True
        assert normalizer.is_valid_whatsapp_format("https://t.me/testgroup") is False

class TestDeduplicator:
    def test_deduplicate(self):
        deduplicator = Deduplicator()
        urls = [
            "https://chat.whatsapp.com/AAAAA",
            "https://chat.whatsapp.com/BBBBB",
            "https://chat.whatsapp.com/AAAAA",
            "https://chat.whatsapp.com/CCCCC",
            "https://chat.whatsapp.com/BBBBB"
        ]
        unique = deduplicator.deduplicate(urls)
        assert len(unique) == 3
        assert "https://chat.whatsapp.com/AAAAA" in unique
        assert "https://chat.whatsapp.com/BBBBB" in unique
        assert "https://chat.whatsapp.com/CCCCC" in unique

    def test_is_duplicate(self):
        deduplicator = Deduplicator()
        url = "https://chat.whatsapp.com/AAAAA"
        deduplicator.add_url(url)
        assert deduplicator.is_duplicate(url) is True
        assert deduplicator.is_duplicate("https://chat.whatsapp.com/BBBBB") is False