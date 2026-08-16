from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.core.config import settings
from app.bot.middlewares.auth import AuthMiddleware
from app.bot.middlewares.rate_limit import RateLimitMiddleware
from app.bot.middlewares.logging import LoggingMiddleware
from app.bot.middlewares.error_handler import ErrorHandlerMiddleware
from app.bot.middlewares.security import SecurityMiddleware

from app.bot.handlers import (
    start,
    explorer,
    scanner,
    wallet,
    accounts,
    settings,
    jobs,
    export,
    whatsapp_send,
    admin
)

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.message.middleware(SecurityMiddleware())
dp.message.middleware(AuthMiddleware())
dp.message.middleware(RateLimitMiddleware())
dp.message.middleware(LoggingMiddleware())
dp.message.middleware(ErrorHandlerMiddleware())

dp.callback_query.middleware(SecurityMiddleware())
dp.callback_query.middleware(AuthMiddleware())
dp.callback_query.middleware(RateLimitMiddleware())
dp.callback_query.middleware(LoggingMiddleware())
dp.callback_query.middleware(ErrorHandlerMiddleware())

dp.include_router(start.router)
dp.include_router(explorer.router)
dp.include_router(scanner.router)
dp.include_router(wallet.router)
dp.include_router(accounts.router)
dp.include_router(settings.router)
dp.include_router(jobs.router)
dp.include_router(export.router)
dp.include_router(whatsapp_send.router)
dp.include_router(admin.router)

async def set_commands():
    commands = [
        BotCommand(command="start", description="بدء البوت والقائمة الرئيسية"),
        BotCommand(command="help", description="المساعدة"),
        BotCommand(command="explore", description="استكشاف روابط WhatsApp"),
        BotCommand(command="wallet", description="عرض المحفظة"),
        BotCommand(command="jobs", description="عرض المهام الحالية"),
        BotCommand(command="settings", description="الإعدادات"),
        BotCommand(command="admin", description="لوحة الإدارة")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

async def on_startup():
    await set_commands()

async def on_shutdown():
    await bot.session.close()
    
