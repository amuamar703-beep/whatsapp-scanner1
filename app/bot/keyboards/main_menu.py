from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 استكشاف روابط", callback_data="explore:start")
    )
    builder.row(
        InlineKeyboardButton(text="💼 محفظتي", callback_data="wallet:open"),
        InlineKeyboardButton(text="📱 حساباتي", callback_data="accounts:open")
    )
    builder.row(
        InlineKeyboardButton(text="📊 المهام", callback_data="jobs:open"),
        InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="settings:open")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ المساعدة", callback_data="help:open")
    )
    return builder.as_markup()

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