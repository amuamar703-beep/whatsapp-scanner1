from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
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

def main_menu_with_back(callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu:back")
    )
    return builder.as_markup()

def back_button(callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=callback)
    )
    return builder.as_markup()
