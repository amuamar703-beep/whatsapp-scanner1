from typing import Optional, Tuple, Dict, Any
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User, InputPeerChannel
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import GetChatFullRequest, ImportChatInviteRequest
from telethon.errors import (
    ChannelPrivateError,
    ChannelInvalidError,
    ChatAdminRequiredError,
    InviteHashInvalidError,
    InviteHashExpiredError,
    UserAlreadyParticipantError,
    FloodWaitError as TelethonFloodWaitError
)

from app.core.enums import AccessStatus
from app.userbot.exceptions import ResolverError, AccessDeniedError, FloodWaitError

class AccessChecker:
    @classmethod
    async def check_access(cls, client: TelegramClient, entity, source_info: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "access_status": AccessStatus.UNKNOWN,
            "can_read_messages": False,
            "requires_join": False,
            "requires_request": False,
            "is_private": False,
            "is_restricted": False,
            "details": {}
        }

        try:
            if entity is None:
                result["access_status"] = AccessStatus.NOT_FOUND
                return result

            result["details"]["entity_type"] = source_info.get("type", "unknown")
            result["details"]["entity_id"] = entity.id

            if source_info.get("type") == "user":
                result["access_status"] = AccessStatus.ACCESSIBLE
                result["can_read_messages"] = True
                return result

            me = await client.get_me()
            if not me:
                result["access_status"] = AccessStatus.RESTRICTED
                return result

            try:
                if isinstance(entity, Channel):
                    full_chat = await client(GetFullChannelRequest(entity))
                    result["details"]["participants_count"] = getattr(full_chat.full_chat, "participants_count", 0)
                    result["details"]["is_megagroup"] = getattr(full_chat.full_chat, "megagroup", False)
                elif isinstance(entity, Chat):
                    full_chat = await client(GetChatFullRequest(entity.id))
                    result["details"]["participants_count"] = getattr(full_chat.full_chat, "participants_count", 0)

                try:
                    if isinstance(entity, Channel):
                        messages = await client.get_messages(entity, limit=1)
                    else:
                        messages = await client.get_messages(entity, limit=1)
                    
                    if messages is not None:
                        result["access_status"] = AccessStatus.ACCESSIBLE
                        result["can_read_messages"] = True
                        return result

                except (ChannelPrivateError, ChannelInvalidError) as e:
                    result["is_private"] = True
                    
                    try:
                        if isinstance(entity, Channel):
                            join_result = await client(JoinChannelRequest(entity))
                            result["details"]["join_result"] = "success"
                            result["access_status"] = AccessStatus.JOINABLE
                            result["requires_join"] = True
                        else:
                            result["access_status"] = AccessStatus.REQUEST_REQUIRED
                            result["requires_request"] = True
                    except UserAlreadyParticipantError:
                        result["access_status"] = AccessStatus.ACCESSIBLE
                        result["can_read_messages"] = True
                    except ChatAdminRequiredError:
                        result["access_status"] = AccessStatus.REQUEST_REQUIRED
                        result["requires_request"] = True
                    except Exception:
                        result["access_status"] = AccessStatus.REQUEST_REQUIRED
                        result["requires_request"] = True
                    return result

            except (ChannelPrivateError, ChannelInvalidError) as e:
                result["is_private"] = True
                result["access_status"] = AccessStatus.PRIVATE
                result["details"]["error"] = str(e)
                return result

            except TelethonFloodWaitError as e:
                raise FloodWaitError(e.seconds)

            except Exception as e:
                result["access_status"] = AccessStatus.UNKNOWN
                result["details"]["error"] = str(e)
                return result

        except (ChannelPrivateError, ChannelInvalidError) as e:
            result["is_private"] = True
            result["access_status"] = AccessStatus.PRIVATE
            result["details"]["error"] = str(e)
            return result

        except TelethonFloodWaitError as e:
            raise FloodWaitError(e.seconds)

        except Exception as e:
            result["access_status"] = AccessStatus.UNKNOWN
            result["details"]["error"] = str(e)
            return result

        return result

    @classmethod
    async def check_invite_access(cls, client: TelegramClient, invite_hash: str) -> Dict[str, Any]:
        result = {
            "access_status": AccessStatus.UNKNOWN,
            "can_read_messages": False,
            "requires_request": False,
            "is_private": False,
            "details": {}
        }

        try:
            try:
                entity = await client.get_entity(f"https://t.me/+{invite_hash}")
                if entity:
                    result["details"]["entity_id"] = entity.id
                    result["access_status"] = AccessStatus.JOINABLE
                    result["can_read_messages"] = False
                    result["requires_join"] = True
                    return result
            except InviteHashInvalidError:
                result["access_status"] = AccessStatus.INVALID
                result["details"]["error"] = "Invalid invite hash"
                return result
            except InviteHashExpiredError:
                result["access_status"] = AccessStatus.INVALID
                result["details"]["error"] = "Expired invite hash"
                return result
            except ChannelPrivateError:
                result["access_status"] = AccessStatus.REQUEST_REQUIRED
                result["requires_request"] = True
                return result
            except Exception:
                result["access_status"] = AccessStatus.UNKNOWN
                return result

        except InviteHashInvalidError:
            result["access_status"] = AccessStatus.INVALID
            result["details"]["error"] = "Invalid invite hash"
        except InviteHashExpiredError:
            result["access_status"] = AccessStatus.INVALID
            result["details"]["error"] = "Expired invite hash"
        except Exception as e:
            result["access_status"] = AccessStatus.UNKNOWN
            result["details"]["error"] = str(e)

        return result