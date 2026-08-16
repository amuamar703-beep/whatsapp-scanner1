import re
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urlparse, urlunparse, parse_qs

from telethon.tl.types import Message, MessageEntityUrl, MessageEntityTextUrl
from telethon.tl.custom import Message as CustomMessage

from app.userbot.exceptions import ExtractorError, NormalizerError

class URLExtractor:
    WHATSAPP_PATTERNS = [
        re.compile(r'^https?://chat\.whatsapp\.com/([a-zA-Z0-9_-]{22,})$'),
        re.compile(r'^https?://wa\.me/(\+?\d+)$'),
        re.compile(r'^https?://api\.whatsapp\.com/send\?phone=(\+?\d+)'),
        re.compile(r'^https?://www\.whatsapp\.com/channel/([a-zA-Z0-9_-]+)')
    ]

    def __init__(self):
        self._extracted_urls: Set[str] = set()

    def extract_from_message(self, message: Message) -> List[str]:
        urls = []
        
        if not message or not hasattr(message, 'entities'):
            return urls

        if message.entities:
            for entity in message.entities:
                if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                    try:
                        offset = entity.offset
                        length = entity.length
                        if hasattr(message, 'text') and message.text:
                            url = message.text[offset:offset + length]
                            if url and url.startswith(('http://', 'https://')):
                                urls.append(url)
                    except Exception:
                        continue

        if hasattr(message, 'text') and message.text:
            url_pattern = re.compile(r'https?://[^\s<>"\']+')
            found_urls = url_pattern.findall(message.text)
            urls.extend(found_urls)

        return self._normalize_urls(urls)

    def extract_from_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        url_pattern = re.compile(r'https?://[^\s<>"\']+')
        urls = url_pattern.findall(text)
        return self._normalize_urls(urls)

    def extract_from_entities(self, text: str, entities: List) -> List[str]:
        urls = []
        if not entities:
            return urls

        for entity in entities:
            if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                try:
                    offset = entity.offset
                    length = entity.length
                    if text:
                        url = text[offset:offset + length]
                        if url and url.startswith(('http://', 'https://')):
                            urls.append(url)
                except Exception:
                    continue

        return self._normalize_urls(urls)

    def _normalize_urls(self, urls: List[str]) -> List[str]:
        unique_urls = []
        seen = set()
        for url in urls:
            if not url or url in seen:
                continue
            try:
                parsed = urlparse(url)
                if parsed.scheme and parsed.netloc:
                    normalized = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        '',
                        '',
                        ''
                    ))
                    if normalized not in seen:
                        seen.add(normalized)
                        unique_urls.append(normalized)
            except Exception:
                continue
        return unique_urls

    def extract_whatsapp_urls(self, urls: List[str]) -> List[str]:
        whatsapp_urls = []
        seen = set()

        for url in urls:
            if url in seen:
                continue
            
            is_whatsapp = False
            for pattern in self.WHATSAPP_PATTERNS:
                if pattern.match(url):
                    is_whatsapp = True
                    break

            if is_whatsapp:
                whatsapp_urls.append(url)
                seen.add(url)

        return whatsapp_urls

    def detect_whatsapp_url(self, url: str) -> bool:
        for pattern in self.WHATSAPP_PATTERNS:
            if pattern.match(url):
                return True
        return False

    def extract_invite_hash(self, url: str) -> Optional[str]:
        pattern = re.compile(r'^https?://chat\.whatsapp\.com/([a-zA-Z0-9_-]{22,})$')
        match = pattern.match(url)
        if match:
            return match.group(1)
        return None