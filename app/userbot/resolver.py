import re
from typing import Optional, Tuple, Dict, Any
from telethon import TelegramClient
from telethon.tl.types import (
    Channel,
    Chat,
    User,
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetChatFullRequest
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
    ChatAdminRequiredError
)

from app.userbot.exceptions import ResolverError, SourceNotFoundError, SourceInvalidError

class SourceResolver:
    PATTERN_USERNAME = re.compile(r'^@?[a-zA-Z][a-zA-Z0-9_]{4,31}$')
    PATTERN_ID = re.compile(r'^-?100?\d+$')
    PATTERN_PUBLIC_URL = re.compile(r'^https?://t\.me/([a-zA-Z][a-zA-Z0-9_]{4,31})(?:\?.*)?$')
    PATTERN_PRIVATE_URL_OLD = re.compile(r'^https?://t\.me/joinchat/([a-zA-Z0-9_-]+)(?:\?.*)?$')
    PATTERN_PRIVATE_URL_NEW = re.compile(r'^https?://t\.me/\+([a-zA-Z0-9_-]+)(?:\?.*)?$')

    @classmethod
    def parse_input(cls, input_text: str) -> Dict[str, Any]:
        input_text = input_text.strip()
        
        if cls.PATTERN_PUBLIC_URL.match(input_text):
            match = cls.PATTERN_PUBLIC_URL.match(input_text)
            return {"type": "username", "value": match.group(1)}
        
        if cls.PATTERN_PRIVATE_URL_OLD.match(input_text):
            match = cls.PATTERN_PRIVATE_URL_OLD.match(input_text)
            return {"type": "invite_hash", "value": match.group(1)}
        
        if cls.PATTERN_PRIVATE_URL_NEW.match(input_text):
            match = cls.PATTERN_PRIVATE_URL_NEW.match(input_text)
            return {"type": "invite_hash", "value": match.group(1)}
        
        if cls.PATTERN_USERNAME.match(input_text):
            username = input_text
            if username.startswith('@'):
                username = username[1:]
            return {"type": "username", "value": username}
        
        if cls.PATTERN_ID.match(input_text):
            try:
                chat_id = int(input_text)
                return {"type": "id", "value": chat_id}
            except ValueError:
                pass
        
        return {"type": "unknown", "value": input_text}

    @classmethod
    async def resolve_username(cls, client: TelegramClient, username: str) -> Tuple[Optional[Any], Dict[str, Any]]:
        try:
            entity = await client.get_entity(username)
            info = cls._get_entity_info(entity)
            return entity, info
        except (UsernameInvalidError, UsernameNotOccupiedError):
            raise SourceNotFoundError(f"Username '{username}' not found")
        except (ChannelPrivateError, ChannelInvalidError) as e:
            info = {"type": "private", "error": str(e)}
            return None, info
        except Exception as e:
            raise ResolverError(f"Failed to resolve username '{username}': {e}")

    @classmethod
    async def resolve_id(cls, client: TelegramClient, chat_id: int) -> Tuple[Optional[Any], Dict[str, Any]]:
        try:
            entity = await client.get_entity(chat_id)
            info = cls._get_entity_info(entity)
            return entity, info
        except (ChannelPrivateError, ChannelInvalidError) as e:
            info = {"type": "private", "error": str(e)}
            return None, info
        except Exception as e:
            raise ResolverError(f"Failed to resolve ID '{chat_id}': {e}")

    @classmethod
    async def resolve_invite(cls, client: TelegramClient, invite_hash: str) -> Tuple[Optional[Any], Dict[str, Any]]:
        try:
            updates = await client.get_entity(f"https://t.me/+{invite_hash}")
            if updates:
                entity = await client.get_entity(f"https://t.me/+{invite_hash}")
                info = cls._get_entity_info(entity)
                return entity, info
        except (ChannelPrivateError, ChannelInvalidError) as e:
            info = {"type": "private", "error": str(e)}
            return None, info
        except Exception as e:
            raise ResolverError(f"Failed to resolve invite hash '{invite_hash}': {e}")
        return None, {"type": "not_found"}

    @classmethod
    async def resolve(cls, client: TelegramClient, input_text: str) -> Tuple[Optional[Any], Dict[str, Any]]:
        parsed = cls.parse_input(input_text)
        
        if parsed["type"] == "username":
            return await cls.resolve_username(client, parsed["value"])
        
        if parsed["type"] == "id":
            return await cls.resolve_id(client, parsed["value"])
        
        if parsed["type"] == "invite_hash":
            return await cls.resolve_invite(client, parsed["value"])
        
        return None, {"type": "unknown", "error": "Unable to parse input"}

    @classmethod
    def _get_entity_info(cls, entity) -> Dict[str, Any]:
        info = {
            "id": entity.id,
            "type": "unknown"
        }
        
        if isinstance(entity, Channel):
            info["type"] = "supergroup" if entity.megagroup else "channel"
            info["title"] = entity.title
            info["username"] = entity.username
            info["broadcast"] = getattr(entity, "broadcast", False)
            info["megagroup"] = getattr(entity, "megagroup", False)
            
        elif isinstance(entity, Chat):
            info["type"] = "group"
            info["title"] = entity.title
            info["username"] = None
            
        elif isinstance(entity, User):
            info["type"] = "user"
            info["first_name"] = entity.first_name
            info["last_name"] = entity.last_name
            info["username"] = entity.username
            info["bot"] = getattr(entity, "bot", False)
            
        return info