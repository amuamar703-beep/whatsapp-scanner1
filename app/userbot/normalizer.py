from typing import Optional
from urllib.parse import urlparse, urlunparse, quote, unquote

from app.userbot.exceptions import NormalizerError

class URLNormalizer:
    def __init__(self):
        self._schemes = ['http', 'https']

    def normalize(self, url: str) -> str:
        try:
            if not url:
                raise NormalizerError("Empty URL provided")

            url = url.strip()
            parsed = urlparse(url)

            if not parsed.scheme:
                url = f"https://{url}"
                parsed = urlparse(url)

            scheme = parsed.scheme.lower()
            if scheme not in self._schemes:
                scheme = 'https'

            netloc = parsed.netloc.lower()
            netloc = self._normalize_netloc(netloc)

            path = self._normalize_path(parsed.path)
            
            normalized = urlunparse((
                scheme,
                netloc,
                path,
                '',
                '',
                ''
            ))

            if normalized.endswith('?'):
                normalized = normalized[:-1]

            return normalized

        except Exception as e:
            raise NormalizerError(f"Failed to normalize URL '{url}': {e}")

    def normalize_whatsapp(self, url: str) -> Optional[str]:
        try:
            normalized = self.normalize(url)
            
            parsed = urlparse(normalized)
            if parsed.netloc != 'chat.whatsapp.com':
                return None

            path_parts = parsed.path.split('/')
            if len(path_parts) < 2:
                return None

            invite_hash = path_parts[-1]
            if len(invite_hash) < 22:
                return None

            invite_hash = self._sanitize_hash(invite_hash)

            return f"https://chat.whatsapp.com/{invite_hash}"

        except Exception:
            return None

    def _normalize_netloc(self, netloc: str) -> str:
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        if netloc == 'chat.whatsapp.com':
            return netloc
        return netloc

    def _normalize_path(self, path: str) -> str:
        if not path:
            return '/'
        
        if path.startswith('/.'):
            parts = path.split('/')
            normalized_parts = []
            for part in parts:
                if part and part != '.':
                    if part == '..':
                        if normalized_parts:
                            normalized_parts.pop()
                    else:
                        normalized_parts.append(part)
            
            path = '/' + '/'.join(normalized_parts) if normalized_parts else '/'
        
        return path

    def _sanitize_hash(self, invite_hash: str) -> str:
        import re
        return re.sub(r'[^a-zA-Z0-9_-]', '', invite_hash)

    def is_valid_whatsapp_format(self, url: str) -> bool:
        try:
            normalized = self.normalize(url)
            parsed = urlparse(normalized)
            
            if parsed.netloc != 'chat.whatsapp.com':
                return False
            
            path_parts = parsed.path.split('/')
            if len(path_parts) < 2:
                return False
            
            invite_hash = path_parts[-1]
            return len(invite_hash) >= 22
        except Exception:
            return False