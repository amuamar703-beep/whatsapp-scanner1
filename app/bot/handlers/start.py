from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔍 استكشاف روابط", callback_data="explore:start")
    )
    keyboard.add(
        InlineKeyboardButton("💼 محفظتي", callback_data="wallet:open"),
        InlineKeyboardButton("📱 حساباتي", callback_data="accounts:open")
    )
    keyboard.add(
        InlineKeyboardButton("📊 المهام", callback_data="jobs:open"),
        InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings:open")
    )
    keyboard.add(
        InlineKeyboardButton("ℹ️ المساعدة", callback_data="help:open")
    )
    return keyboard

async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 أهلاً بك في WhatsApp Link Scanner\n\n"
        "يمكنك من هنا:\n"
        "• استكشاف روابط WhatsApp من مصادر Telegram\n"
        "• فحص صلاحية الروابط وتصنيفها\n"
        "• حفظ الروابط في محفظتك\n"
        "• تصدير الروابط\n"
        "• إدارة حسابات WhatsApp\n\n"
        "اختر العملية التي تريدها:"
    )
    await message.reply(welcome_text, reply_markup=main_menu_keyboard())

async def cmd_help(message: types.Message):
    help_text = (
        "📖 المساعدة\n\n"
        "الأوامر المتاحة:\n"
        "/start - القائمة الرئيسية\n"
        "/help - المساعدة\n"
        "/explore - استكشاف روابط WhatsApp\n"
        "/wallet - عرض المحفظة\n"
        "/jobs - عرض المهام الحالية\n"
        "/settings - الإعدادات\n\n"
        "للاستفسارات والدعم، يرجى التواصل مع المطور."
    )
    await message.reply(help_text)

async def cmd_explore(message: types.Message):
    from app.bot.handlers.explorer import start_exploration
    await start_exploration(message)

async def cmd_wallet(message: types.Message):
    from app.bot.handlers.wallet import open_wallet
    await open_wallet(message)

async def cmd_jobs(message: types.Message):
    from app.bot.handlers.jobs import view_jobs
    await view_jobs(message)

async def cmd_settings(message: types.Message):
    from app.bot.handlers.settings import open_settings
    await open_settings(message)

async def cmd_admin(message: types.Message):
    from app.bot.handlers.admin import admin_panel
    await admin_panel(message)
