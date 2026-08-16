from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime

from app.userbot.exceptions import DeduplicatorError

class Deduplicator:
    def __init__(self):
        self._seen_urls: Set[str] = set()
        self._url_index: Dict[str, List[Dict]] = defaultdict(list)

    def deduplicate(self, urls: List[str]) -> List[str]:
        unique_urls = []
        for url in urls:
            if self.is_duplicate(url):
                continue
            
            self._seen_urls.add(url)
            unique_urls.append(url)
        
        return unique_urls

    def process_with_metadata(
        self,
        urls_with_metadata: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        unique_items = []
        seen = set()

        for item in urls_with_metadata:
            url = item.get('url', '')
            if not url or url in seen:
                continue

            canonical_url = self._get_canonical_url(url)
            if canonical_url and canonical_url in seen:
                continue

            if canonical_url:
                item['canonical_url'] = canonical_url
                seen.add(canonical_url)
            else:
                seen.add(url)

            unique_items.append(item)

        return unique_items

    def is_duplicate(self, url: str) -> bool:
        if url in self._seen_urls:
            return True
        
        canonical = self._get_canonical_url(url)
        if canonical and canonical in self._seen_urls:
            return True
        
        return False

    def add_url(self, url: str):
        self._seen_urls.add(url)

    def add_urls(self, urls: List[str]):
        for url in urls:
            self._seen_urls.add(url)

    def _get_canonical_url(self, url: str) -> Optional[str]:
        try:
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return None
            
            canonical = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip('/'),
                '',
                '',
                ''
            ))
            
            return canonical
        except Exception:
            return None

    def get_stats(self) -> Dict[str, int]:
        return {
            "total_urls": len(self._seen_urls),
            "unique_urls": len(self._seen_urls)
        }

    def clear(self):
        self._seen_urls.clear()
        self._url_index.clear()

    def get_url_info(self, url: str) -> List[Dict]:
        canonical = self._get_canonical_url(url)
        if canonical and canonical in self._url_index:
            return self._url_index[canonical]
        return []