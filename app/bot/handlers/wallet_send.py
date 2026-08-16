from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

def wallet_send_whatsapp_keyboard(direct_url: str, links: list, category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📱 فتح WhatsApp",
            url=direct_url
        )
    )
    
    links_data = json.dumps(links[:20])
    
    builder.row(
        InlineKeyboardButton(
            text="📋 نسخ الروابط",
            callback_data=f"whatsapp:copy:{category}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="wallet:back")
    )
    
    return builder.as_markup()