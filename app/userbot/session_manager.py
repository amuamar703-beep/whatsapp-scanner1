import json
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings
from app.userbot.exceptions import SessionError, SessionExpiredError, SessionInvalidError

class SessionManager:
    def __init__(self):
        self._fernet = self._create_fernet()

    def _create_fernet(self) -> Fernet:
        try:
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
        except Exception as e:
            raise SessionError(f"Failed to initialize encryption: {e}")

    def encrypt_session(self, session_data: Dict[str, Any]) -> str:
        try:
            json_data = json.dumps(session_data)
            encrypted = self._fernet.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise SessionError(f"Failed to encrypt session: {e}")

    def decrypt_session(self, encrypted_data: str) -> Dict[str, Any]:
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            data = json.loads(decrypted.decode())
            return data
        except Exception as e:
            raise SessionError(f"Failed to decrypt session: {e}")

    def create_session_string(self, client) -> str:
        try:
            session_string = client.session.save()
            return session_string
        except Exception as e:
            raise SessionError(f"Failed to create session string: {e}")

    def load_session_from_string(self, session_string: str):
        from telethon.sessions import StringSession
        try:
            return StringSession(session_string)
        except Exception as e:
            raise SessionInvalidError(f"Invalid session string: {e}")

    def validate_session_string(self, session_string: str) -> bool:
        try:
            from telethon.sessions import StringSession
            StringSession(session_string)
            return True
        except Exception:
            return False

    def get_session_data(self, encrypted_data: str) -> Dict[str, Any]:
        data = self.decrypt_session(encrypted_data)
        if not self.validate_session_string(data.get("session_string", "")):
            raise SessionInvalidError("Invalid session string in encrypted data")
        return data

    def pack_session(self, session_string: str, phone: str = None, user_id: int = None) -> str:
        data = {
            "session_string": session_string,
            "phone": phone,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        return self.encrypt_session(data)