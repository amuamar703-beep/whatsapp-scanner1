from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.enums import LinkStatus, ConfidenceLevel

class AnalysisResult:
    def __init__(
        self,
        url: str,
        status: LinkStatus,
        confidence: ConfidenceLevel = ConfidenceLevel.LOW,
        details: Optional[Dict[str, Any]] = None,
        checked_at: Optional[datetime] = None
    ):
        self.url = url
        self.status = status
        self.confidence = confidence
        self.details = details or {}
        self.checked_at = checked_at or datetime.now()
        self.is_valid = self._validate()

    def _validate(self) -> bool:
        if self.status in [
            LinkStatus.DIRECT_JOIN,
            LinkStatus.REQUEST_JOIN,
            LinkStatus.INVALID,
            LinkStatus.REVOKED_OR_CHANGED,
            LinkStatus.TEMPORARY_ERROR,
            LinkStatus.UNKNOWN
        ]:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "details": self.details,
            "checked_at": self.checked_at.isoformat()
        }

class BaseAnalyzer(ABC):
    def __init__(self):
        self._last_analysis_time = None
        self._analysis_count = 0

    @abstractmethod
    async def analyze(self, url: str) -> AnalysisResult:
        pass

    @abstractmethod
    async def analyze_batch(self, urls: list) -> list:
        pass

    @abstractmethod
    async def can_analyze(self, url: str) -> bool:
        pass

    def get_stats(self) -> Dict[str, Any]:
        return {
            "analysis_count": self._analysis_count,
            "last_analysis_time": self._last_analysis_time
        }

    def _increment_count(self):
        self._analysis_count += 1
        self._last_analysis_time = datetime.now()