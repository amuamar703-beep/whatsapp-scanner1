from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            logger.info(
                f"Message from {event.from_user.id}: "
                f"text='{event.text or '[non-text]'}'"
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"Callback from {event.from_user.id}: "
                f"data='{event.data}'"
            )

        return await handler(event, data)