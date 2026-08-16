from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.security import security_manager
from app.core.exceptions import SessionError

class SessionValidator:
    @staticmethod
    def validate_session_string(session_string: str) -> bool:
        try:
            from telethon.sessions import StringSession
            StringSession(session_string)
            return True
        except Exception:
            return False

    @staticmethod
    def validate_encrypted_session(encrypted_data: str) -> Dict[str, Any]:
        try:
            data = security_manager.decrypt(encrypted_data)
            if not data:
                raise SessionError("Failed to decrypt session data")
            import json
            session_data = json.loads(data)
            required_keys = ["session_string", "created_at"]
            for key in required_keys:
                if key not in session_data:
                    raise SessionError(f"Missing required key: {key}")
            if not SessionValidator.validate_session_string(session_data["session_string"]):
                raise SessionError("Invalid session string")
            return session_data
        except json.JSONDecodeError:
            raise SessionError("Invalid session data format")
        except Exception as e:
            raise SessionError(f"Session validation error: {e}")

    @staticmethod
    def is_session_expired(encrypted_data: str, max_age_days: int = 7) -> bool:
        try:
            data = SessionValidator.validate_encrypted_session(encrypted_data)
            created_at = datetime.fromisoformat(data.get("created_at"))
            return datetime.now() - created_at > timedelta(days=max_age_days)
        except Exception:
            return True

    @staticmethod
    def get_session_age(encrypted_data: str) -> Optional[float]:
        try:
            data = SessionValidator.validate_encrypted_session(encrypted_data)
            created_at = datetime.fromisoformat(data.get("created_at"))
            return (datetime.now() - created_at).total_seconds()
        except Exception:
            return None