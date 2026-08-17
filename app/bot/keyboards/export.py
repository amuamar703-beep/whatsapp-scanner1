from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def export_format_keyboard(job_id: str, category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📄 TXT", callback_data=f"export:format:{job_id}:txt:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("📊 CSV", callback_data=f"export:format:{job_id}:csv:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("📋 JSON", callback_data=f"export:format:{job_id}:json:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return keyboard

def export_wallet_format_keyboard(category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📄 TXT", callback_data=f"export:wallet_format:{category}:txt")
    )
    keyboard.add(
        InlineKeyboardButton("📊 CSV", callback_data=f"export:wallet_format:{category}:csv")
    )
    keyboard.add(
        InlineKeyboardButton("📋 JSON", callback_data=f"export:wallet_format:{category}:json")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="wallet:back")
    )
    return keyboard
