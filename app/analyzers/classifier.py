from typing import Dict, Any, Optional
import re

from app.core.enums import LinkStatus, ConfidenceLevel
from app.analyzers.exceptions import ClassifierError

class Classifier:
    def __init__(self):
        self._classification_rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict:
        return {
            "direct_join": {
                "patterns": [
                    re.compile(r'^https?://chat\.whatsapp\.com/[a-zA-Z0-9_-]{22,}$'),
                ],
                "status_codes": [200, 301, 302],
                "confidence": ConfidenceLevel.HIGH
            },
            "request_join": {
                "patterns": [
                    re.compile(r'^https?://chat\.whatsapp\.com/[a-zA-Z0-9_-]{22,}$'),
                ],
                "status_codes": [403],
                "confidence": ConfidenceLevel.MEDIUM
            },
            "invalid": {
                "status_codes": [404, 410],
                "confidence": ConfidenceLevel.HIGH
            },
            "revoked_or_changed": {
                "status_codes": [410],
                "confidence": ConfidenceLevel.HIGH
            },
            "temporary_error": {
                "status_codes": [429, 500, 502, 503, 504],
                "confidence": ConfidenceLevel.MEDIUM
            }
        }

    async def classify(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            status_code = data.get("status_code")
            final_url = data.get("final_url", url)
            headers = data.get("headers", {})

            if self._is_direct_join(url, status_code, final_url):
                return {
                    "status": LinkStatus.DIRECT_JOIN,
                    "confidence": ConfidenceLevel.HIGH,
                    "details": {"status_code": status_code, "final_url": final_url}
                }

            if self._is_request_join(status_code, headers):
                return {
                    "status": LinkStatus.REQUEST_JOIN,
                    "confidence": ConfidenceLevel.MEDIUM,
                    "details": {"status_code": status_code}
                }

            if self._is_invalid(status_code):
                return {
                    "status": LinkStatus.INVALID,
                    "confidence": ConfidenceLevel.HIGH,
                    "details": {"status_code": status_code}
                }

            if self._is_revoked(status_code):
                return {
                    "status": LinkStatus.REVOKED_OR_CHANGED,
                    "confidence": ConfidenceLevel.HIGH,
                    "details": {"status_code": status_code}
                }

            if self._is_temporary_error(status_code):
                return {
                    "status": LinkStatus.TEMPORARY_ERROR,
                    "confidence": ConfidenceLevel.MEDIUM,
                    "details": {"status_code": status_code}
                }

            return {
                "status": LinkStatus.UNKNOWN,
                "confidence": ConfidenceLevel.LOW,
                "details": {"status_code": status_code}
            }

        except Exception as e:
            raise ClassifierError(f"Classification failed: {e}")

    def _is_direct_join(self, url: str, status_code: int, final_url: str) -> bool:
        if status_code in self._classification_rules["direct_join"]["status_codes"]:
            pattern = re.compile(r'^https?://chat\.whatsapp\.com/[a-zA-Z0-9_-]{22,}$')
            if pattern.match(url):
                return True
        return False

    def _is_request_join(self, status_code: int, headers: Dict) -> bool:
        if status_code == 403:
            return True
        
        if status_code == 200:
            content_type = headers.get("content-type", "").lower()
            if "whatsapp" in content_type:
                return True
        
        return False

    def _is_invalid(self, status_code: int) -> bool:
        return status_code in [404]

    def _is_revoked(self, status_code: int) -> bool:
        return status_code == 410

    def _is_temporary_error(self, status_code: int) -> bool:
        return status_code in [429, 500, 502, 503, 504]

    async def classify_batch(self, urls_data: list) -> list:
        results = []
        for url_data in urls_data:
            result = await self.classify(
                url_data.get("url"),
                url_data.get("data", {})
            )
            results.append(result)
        return results