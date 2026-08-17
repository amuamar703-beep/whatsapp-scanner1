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

def main_menu_with_back(callback: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🏠 الرئيسية", callback_data=callback)
    )
    return keyboard

def back_button(callback: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=callback)
    )
    return keyboard
