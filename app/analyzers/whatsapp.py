import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import re

from app.core.enums import LinkStatus, ConfidenceLevel
from app.analyzers.base import BaseAnalyzer, AnalysisResult
from app.analyzers.classifier import Classifier
from app.analyzers.validator import ResultValidator
from app.analyzers.retry_manager import RetryManager
from app.analyzers.rate_limiter import RateLimiter
from app.analyzers.adapters.official_adapter import OfficialAdapter
from app.analyzers.exceptions import AnalysisFailedError, AnalysisTimeoutError

class WhatsAppAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.classifier = Classifier()
        self.validator = ResultValidator()
        self.retry_manager = RetryManager()
        self.rate_limiter = RateLimiter()
        self.official_adapter = OfficialAdapter()
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return self._session

    async def analyze(self, url: str) -> AnalysisResult:
        await self.rate_limiter.acquire()
        
        try:
            result = await self.retry_manager.execute(
                self._perform_analysis,
                url
            )
            self._increment_count()
            return result
        except Exception as e:
            return AnalysisResult(
                url=url,
                status=LinkStatus.TEMPORARY_ERROR,
                confidence=ConfidenceLevel.LOW,
                details={"error": str(e)}
            )

    async def analyze_batch(self, urls: list) -> list:
        results = []
        for url in urls:
            result = await self.analyze(url)
            results.append(result)
        return results

    async def can_analyze(self, url: str) -> bool:
        if not url:
            return False
        
        patterns = [
            re.compile(r'^https?://chat\.whatsapp\.com/[a-zA-Z0-9_-]{22,}$'),
            re.compile(r'^https?://wa\.me/'),
            re.compile(r'^https?://api\.whatsapp\.com/send')
        ]
        
        for pattern in patterns:
            if pattern.match(url):
                return True
        return False

    async def _perform_analysis(self, url: str) -> AnalysisResult:
        session = await self._get_session()
        
        try:
            response = await session.head(
                url,
                allow_redirects=True,
                timeout=20
            )
            
            status_code = response.status
            final_url = str(response.url)
            
            analysis_data = {
                "status_code": status_code,
                "final_url": final_url,
                "headers": dict(response.headers)
            }
            
            return await self._classify_result(url, analysis_data)
            
        except asyncio.TimeoutError:
            return AnalysisResult(
                url=url,
                status=LinkStatus.TEMPORARY_ERROR,
                confidence=ConfidenceLevel.MEDIUM,
                details={"error": "Timeout"}
            )
        except aiohttp.ClientError as e:
            return await self._handle_client_error(url, e)
        except Exception as e:
            return AnalysisResult(
                url=url,
                status=LinkStatus.UNKNOWN,
                confidence=ConfidenceLevel.LOW,
                details={"error": str(e)}
            )

    async def _classify_result(self, url: str, data: Dict[str, Any]) -> AnalysisResult:
        classification = await self.classifier.classify(url, data)
        
        validated = await self.validator.validate(classification)
        
        return AnalysisResult(
            url=url,
            status=validated["status"],
            confidence=validated["confidence"],
            details=validated.get("details", {})
        )

    async def _handle_client_error(self, url: str, error: Exception) -> AnalysisResult:
        error_str = str(error).lower()
        
        if "404" in error_str or "not found" in error_str:
            return AnalysisResult(
                url=url,
                status=LinkStatus.INVALID,
                confidence=ConfidenceLevel.HIGH,
                details={"error": str(error)}
            )
        
        if "403" in error_str or "forbidden" in error_str:
            return AnalysisResult(
                url=url,
                status=LinkStatus.REQUEST_JOIN,
                confidence=ConfidenceLevel.MEDIUM,
                details={"error": str(error)}
            )
        
        if "429" in error_str or "rate" in error_str:
            return AnalysisResult(
                url=url,
                status=LinkStatus.TEMPORARY_ERROR,
                confidence=ConfidenceLevel.MEDIUM,
                details={"error": str(error)}
            )
        
        return AnalysisResult(
            url=url,
            status=LinkStatus.UNKNOWN,
            confidence=ConfidenceLevel.LOW,
            details={"error": str(error)}
        )

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
