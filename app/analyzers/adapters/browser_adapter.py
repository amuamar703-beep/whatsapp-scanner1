import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from app.analyzers.exceptions import AdapterError, AdapterConnectionError, AdapterTimeoutError

class BrowserAdapter:
    def __init__(self):
        self._browser = None
        self._page = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        
        try:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self._page = await self._browser.new_page()
            self._initialized = True
        except ImportError:
            raise AdapterError("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        except Exception as e:
            raise AdapterError(f"Failed to initialize browser: {e}")

    async def check_url(self, url: str) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self._page.goto(
                url,
                wait_until='networkidle',
                timeout=30000
            )
            
            if response is None:
                raise AdapterError("No response received")
            
            content = await self._page.content()
            
            return {
                "status_code": response.status,
                "final_url": response.url,
                "content": content,
                "headers": dict(response.headers),
                "success": True
            }
            
        except asyncio.TimeoutError:
            raise AdapterTimeoutError(f"Timeout checking URL: {url}")
        except Exception as e:
            raise AdapterError(f"Browser error: {e}")

    async def get_join_request_status(self, url: str) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        try:
            await self._page.goto(url, wait_until='networkidle', timeout=30000)
            
            content = await self._page.content()
            
            is_request = False
            is_joinable = False
            
            if "طلب" in content or "request" in content.lower():
                is_request = True
            
            if "انضم" in content or "join" in content.lower():
                if "طلب" not in content and "request" not in content.lower():
                    is_joinable = True
            
            return {
                "requires_request": is_request,
                "is_joinable": is_joinable,
                "content": content[:1000],
                "success": True
            }
            
        except Exception as e:
            return {
                "requires_request": False,
                "is_joinable": False,
                "error": str(e),
                "success": False
            }

    def is_whatsapp_url(self, url: str) -> bool:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        return netloc in ['chat.whatsapp.com', 'wa.me', 'api.whatsapp.com']

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None
            self._initialized = False