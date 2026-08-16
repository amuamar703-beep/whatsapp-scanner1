from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📱 حسابات WhatsApp", callback_data="settings:whatsapp")
    )
    builder.row(
        InlineKeyboardButton(text="👤 حساب Telegram", callback_data="settings:telegram")
    )
    builder.row(
        InlineKeyboardButton(text="📊 إعدادات الاستكشاف", callback_data="settings:exploration")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 الإشعارات", callback_data="settings:notifications")
    )
    builder.row(
        InlineKeyboardButton(text="🌐 اللغة", callback_data="settings:language")
    )
    builder.row(
        InlineKeyboardButton(text="🧹 إدارة البيانات", callback_data="settings:data")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="main_menu:back")
    )
    return builder.as_markup()

def exploration_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📄 عدد الروابط في الصفحة: 20", callback_data="settings:per_page")
    )
    builder.row(
        InlineKeyboardButton(text="📅 نطاق الاستكشاف: كل الرسائل", callback_data="settings:scope")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ الفحص التلقائي: ❌ متوقف", callback_data="settings:auto_scan")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="settings:back")
    )
    return builder.as_markup()

def data_management_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🗑 مسح المهام المكتملة", callback_data="settings:clear_jobs")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 مسح سجل العمليات", callback_data="settings:clear_logs")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 مسح جميع البيانات", callback_data="settings:clear_all")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="settings:back")
    )
    return builder.as_markup()