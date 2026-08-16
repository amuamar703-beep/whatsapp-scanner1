from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.exceptions import TelegramBadRequest

from app.database.database import get_db
from app.database.repositories import UserRepository

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if not user_id:
            return await handler(event, data)

        async with get_db() as db:
            user_repo = UserRepository(db)
            user, created = user_repo.get_or_create(
                user_id,
                username=event.from_user.username,
                first_name=event.from_user.first_name,
                language=event.from_user.language_code
            )

            data["user"] = user
            data["user_id"] = user_id
            data["db"] = db

            return await handler(event, data)