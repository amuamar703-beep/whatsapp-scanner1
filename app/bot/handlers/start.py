from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.bot.keyboards.main_menu import main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
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

@router.message(Command("help"))
async def cmd_help(message: Message):
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

@router.message(Command("explore"))
async def cmd_explore(message: Message):
    from app.bot.handlers.explorer import start_exploration
    await start_exploration(message)

@router.message(Command("wallet"))
async def cmd_wallet(message: Message):
    from app.bot.handlers.wallet import open_wallet
    await open_wallet(message)

@router.message(Command("jobs"))
async def cmd_jobs(message: Message):
    from app.bot.handlers.jobs import view_jobs
    await view_jobs(message)

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    from app.bot.handlers.settings import open_settings
    await open_settings(message)

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    from app.bot.handlers.admin import admin_panel
    await admin_panel(message)