import functools
from typing import Callable, Any
from aiogram.types import Message, CallbackQuery

from app.middleware.rate_limit import rate_limiter
from app.core.exceptions import RateLimitError

def rate_limit(key: str = None, user_identifier: str = "user_id"):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = None

            for arg in args:
                if isinstance(arg, Message):
                    user_id = arg.from_user.id
                elif isinstance(arg, CallbackQuery):
                    user_id = arg.from_user.id

            if user_id is None:
                user_id = kwargs.get(user_identifier)

            if user_id is None:
                return await func(*args, **kwargs)

            rate_key = f"{key}:{user_id}" if key else str(user_id)

            try:
                rate_limiter.check_limit(user_id, rate_key)
                return await func(*args, **kwargs)
            except RateLimitError as e:
                if args and isinstance(args[0], Message):
                    await args[0].reply(f"⏳ {e.message}. يرجى الانتظار.")
                elif args and isinstance(args[0], CallbackQuery):
                    await args[0].answer(f"⏳ {e.message}", show_alert=True)
                raise

        return wrapper
    return decorator