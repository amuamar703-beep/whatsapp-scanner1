from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.enums import LinkStatus, ConfidenceLevel
from app.analyzers.exceptions import ValidatorError

class ResultValidator:
    def __init__(self):
        self._valid_statuses = [
            LinkStatus.DIRECT_JOIN,
            LinkStatus.REQUEST_JOIN,
            LinkStatus.INVALID,
            LinkStatus.REVOKED_OR_CHANGED,
            LinkStatus.TEMPORARY_ERROR,
            LinkStatus.UNKNOWN
        ]

    async def validate(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        try:
            status = classification.get("status")
            confidence = classification.get("confidence")
            details = classification.get("details", {})

            if not status or status not in self._valid_statuses:
                classification["status"] = LinkStatus.UNKNOWN
                classification["confidence"] = ConfidenceLevel.LOW

            if not confidence:
                classification["confidence"] = ConfidenceLevel.LOW

            status_code = details.get("status_code")
            if status_code and isinstance(status_code, int):
                classification["details"]["validated_status_code"] = status_code

            classification["details"]["validated_at"] = datetime.now().isoformat()

            return classification

        except Exception as e:
            raise ValidatorError(f"Validation failed: {e}")

    async def validate_batch(self, classifications: list) -> list:
        return [await self.validate(c) for c in classifications]

    def is_confidence_high(self, result: Dict[str, Any]) -> bool:
        return result.get("confidence") == ConfidenceLevel.HIGH

    def is_confidence_medium(self, result: Dict[str, Any]) -> bool:
        return result.get("confidence") == ConfidenceLevel.MEDIUM

    def is_confidence_low(self, result: Dict[str, Any]) -> bool:
        return result.get("confidence") == ConfidenceLevel.LOW

    def should_retry(self, result: Dict[str, Any]) -> bool:
        status = result.get("status")
        if status == LinkStatus.TEMPORARY_ERROR:
            return True
        if status == LinkStatus.UNKNOWN:
            return True
        if result.get("confidence") == ConfidenceLevel.LOW:
            return True
        return False