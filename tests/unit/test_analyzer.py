import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.analyzers import (
    BaseAnalyzer,
    WhatsAppAnalyzer,
    Classifier,
    ResultValidator,
    RetryManager,
    RateLimiter
)
from app.analyzers.base import AnalysisResult
from app.core.enums import LinkStatus, ConfidenceLevel

class TestAnalysisResult:
    def test_create_analysis_result(self):
        result = AnalysisResult(
            url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            status=LinkStatus.DIRECT_JOIN,
            confidence=ConfidenceLevel.HIGH,
            details={"status_code": 200}
        )
        assert result.url == "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        assert result.status == LinkStatus.DIRECT_JOIN
        assert result.confidence == ConfidenceLevel.HIGH
        assert result.details == {"status_code": 200}
        assert result.is_valid is True

    def test_invalid_status(self):
        result = AnalysisResult(
            url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            status=LinkStatus.DIRECT_JOIN,
            confidence=ConfidenceLevel.HIGH
        )
        assert result.is_valid is True

    def test_to_dict(self):
        result = AnalysisResult(
            url="https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            status=LinkStatus.DIRECT_JOIN,
            confidence=ConfidenceLevel.HIGH,
            details={"status_code": 200}
        )
        data = result.to_dict()
        assert data["url"] == "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        assert data["status"] == "direct_join"
        assert data["confidence"] == "high"
        assert data["details"] == {"status_code": 200}

class TestClassifier:
    @pytest.mark.asyncio
    async def test_classify_direct_join(self):
        classifier = Classifier()
        result = await classifier.classify(
            "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            {"status_code": 200, "final_url": "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        )
        assert result["status"] == LinkStatus.DIRECT_JOIN
        assert result["confidence"] == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_classify_invalid(self):
        classifier = Classifier()
        result = await classifier.classify(
            "https://chat.whatsapp.com/INVALID",
            {"status_code": 404}
        )
        assert result["status"] == LinkStatus.INVALID
        assert result["confidence"] == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_classify_request_join(self):
        classifier = Classifier()
        result = await classifier.classify(
            "https://chat.whatsapp.com/REQUEST",
            {"status_code": 403}
        )
        assert result["status"] == LinkStatus.REQUEST_JOIN
        assert result["confidence"] == ConfidenceLevel.MEDIUM

    @pytest.mark.asyncio
    async def test_classify_temporary_error(self):
        classifier = Classifier()
        result = await classifier.classify(
            "https://chat.whatsapp.com/ERROR",
            {"status_code": 429}
        )
        assert result["status"] == LinkStatus.TEMPORARY_ERROR
        assert result["confidence"] == ConfidenceLevel.MEDIUM

class TestResultValidator:
    @pytest.mark.asyncio
    async def test_validate_valid_result(self):
        validator = ResultValidator()
        result = {
            "status": LinkStatus.DIRECT_JOIN,
            "confidence": ConfidenceLevel.HIGH,
            "details": {"status_code": 200}
        }
        validated = await validator.validate(result)
        assert validated["status"] == LinkStatus.DIRECT_JOIN
        assert validated["confidence"] == ConfidenceLevel.HIGH

    @pytest.mark.asyncio
    async def test_validate_invalid_status(self):
        validator = ResultValidator()
        result = {
            "status": "INVALID_STATUS",
            "details": {}
        }
        validated = await validator.validate(result)
        assert validated["status"] == LinkStatus.UNKNOWN
        assert validated["confidence"] == ConfidenceLevel.LOW

    def test_should_retry(self):
        validator = ResultValidator()
        assert validator.should_retry({"status": LinkStatus.TEMPORARY_ERROR}) is True
        assert validator.should_retry({"status": LinkStatus.UNKNOWN}) is True
        assert validator.should_retry({"status": LinkStatus.DIRECT_JOIN}) is False