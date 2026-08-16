import os
import base64
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings

class SecurityManager:
    def __init__(self):
        self._fernet = self._create_fernet()
        self._secret_key = settings.SECRET_KEY

    def _create_fernet(self) -> Fernet:
        key = settings.ENCRYPTION_KEY
        if len(key) < 32:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"whatsapp_link_scanner_salt",
                iterations=100000,
            )
            key_bytes = kdf.derive(key.encode())
            fernet_key = base64.urlsafe_b64encode(key_bytes)
        else:
            fernet_key = key.encode()
        return Fernet(fernet_key)

    def encrypt(self, data: str) -> str:
        try:
            encrypted = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception:
            return ""

    def decrypt(self, encrypted_data: str) -> str:
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return ""

    def hash_password(self, password: str) -> str:
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return base64.b64encode(salt + key).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        try:
            decoded = base64.b64decode(hashed.encode('utf-8'))
            salt = decoded[:32]
            stored_key = decoded[32:]
            computed_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            )
            return computed_key == stored_key
        except Exception:
            return False

    def generate_token(self, user_id: int, expires_in: int = 86400) -> str:
        timestamp = datetime.now().timestamp()
        token_data = f"{user_id}:{timestamp}:{expires_in}"
        signature = hashlib.sha256(
            f"{token_data}:{self._secret_key}".encode()
        ).hexdigest()
        token = base64.urlsafe_b64encode(
            f"{token_data}:{signature}".encode()
        ).decode()
        return token

    def verify_token(self, token: str) -> Optional[int]:
        try:
            decoded = base64.urlsafe_b64decode(token.encode()).decode()
            parts = decoded.split(':')
            if len(parts) != 4:
                return None

            user_id = int(parts[0])
            timestamp = float(parts[1])
            expires_in = int(parts[2])
            signature = parts[3]

            expected_signature = hashlib.sha256(
                f"{user_id}:{timestamp}:{expires_in}:{self._secret_key}".encode()
            ).hexdigest()

            if signature != expected_signature:
                return None

            if datetime.now().timestamp() - timestamp > expires_in:
                return None

            return user_id
        except Exception:
            return None

    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        if len(data) <= visible_chars * 2:
            return "*" * len(data)
        return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]

    def validate_input(self, input_data: str, max_length: int = 4096) -> bool:
        if not input_data:
            return False
        if len(input_data) > max_length:
            return False
        dangerous_patterns = [
            "javascript:",
            "data:",
            "vbscript:",
            "onclick",
            "onerror",
            "onload",
            "onmouseover"
        ]
        input_lower = input_data.lower()
        for pattern in dangerous_patterns:
            if pattern in input_lower:
                return False
        return True

    def sanitize_filename(self, filename: str) -> str:
        import re
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        filename = filename.strip()
        if not filename:
            filename = "file"
        return filename

security_manager = SecurityManager()