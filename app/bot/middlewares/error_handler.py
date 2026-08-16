from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.exceptions import TelegramBadRequest
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error in handler: {e}\n{traceback.format_exc()}")

            if isinstance(event, Message):
                try:
                    await event.reply("حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى.")
                except TelegramBadRequest:
                    pass
            elif isinstance(event, CallbackQuery):
                try:
                    await event.answer("حدث خطأ أثناء معالجة طلبك", show_alert=True)
                except TelegramBadRequest:
                    pass