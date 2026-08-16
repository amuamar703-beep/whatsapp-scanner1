import aiohttp
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from app.analyzers.exceptions import AdapterError, AdapterConnectionError, AdapterTimeoutError

class OfficialAdapter:
    def __init__(self):
        self._session = None
        self._timeout = 30

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_headers()
            )
        return self._session

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    async def check_url(self, url: str) -> Dict[str, Any]:
        try:
            session = await self._get_session()
            
            response = await session.head(
                url,
                allow_redirects=True,
                timeout=self._timeout
            )
            
            return {
                "status_code": response.status,
                "final_url": str(response.url),
                "headers": dict(response.headers),
                "success": True
            }
            
        except asyncio.TimeoutError:
            raise AdapterTimeoutError(f"Timeout checking URL: {url}")
        except aiohttp.ClientConnectorError:
            raise AdapterConnectionError(f"Connection error for URL: {url}")
        except aiohttp.ClientError as e:
            raise AdapterError(f"Client error: {e}")
        except Exception as e:
            raise AdapterError(f"Unexpected error: {e}")

    async def get_content(self, url: str) -> Dict[str, Any]:
        try:
            session = await self._get_session()
            
            response = await session.get(
                url,
                allow_redirects=True,
                timeout=self._timeout
            )
            
            content = await response.text()
            
            return {
                "status_code": response.status,
                "final_url": str(response.url),
                "content": content,
                "headers": dict(response.headers),
                "success": True
            }
            
        except asyncio.TimeoutError:
            raise AdapterTimeoutError(f"Timeout getting content from: {url}")
        except aiohttp.ClientConnectorError:
            raise AdapterConnectionError(f"Connection error for URL: {url}")
        except aiohttp.ClientError as e:
            raise AdapterError(f"Client error: {e}")
        except Exception as e:
            raise AdapterError(f"Unexpected error: {e}")

    def is_whatsapp_url(self, url: str) -> bool:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        return netloc in ['chat.whatsapp.com', 'wa.me', 'api.whatsapp.com']

    def extract_invite_hash(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        if parsed.netloc.lower() == 'chat.whatsapp.com':
            path_parts = parsed.path.strip('/').split('/')
            if path_parts:
                return path_parts[-1]
        return None

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None