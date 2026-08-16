from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.core.security import security_manager
from app.core.exceptions import ValidationError

class SecurityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            if event.text:
                if not security_manager.validate_input(event.text):
                    await event.reply("⚠️ تم اكتشاف محتوى غير آمن. يرجى التحقق من الإدخال.")
                    return

        return await handler(event, data)