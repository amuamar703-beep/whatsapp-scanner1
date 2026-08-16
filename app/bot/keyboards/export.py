from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def export_format_keyboard(job_id: str, category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📄 TXT", callback_data=f"export:format:{job_id}:txt:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="📊 CSV", callback_data=f"export:format:{job_id}:csv:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="📋 JSON", callback_data=f"export:format:{job_id}:json:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return builder.as_markup()

def export_wallet_format_keyboard(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📄 TXT", callback_data=f"export:wallet_format:{category}:txt")
    )
    builder.row(
        InlineKeyboardButton(text="📊 CSV", callback_data=f"export:wallet_format:{category}:csv")
    )
    builder.row(
        InlineKeyboardButton(text="📋 JSON", callback_data=f"export:wallet_format:{category}:json")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="wallet:back")
    )
    return builder.as_markup()