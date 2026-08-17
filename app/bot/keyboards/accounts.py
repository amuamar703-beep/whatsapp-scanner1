from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def telegram_accounts_keyboard(accounts: List[Dict[str, Any]]):
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for acc in accounts:
        status = "🟢" if acc.get("status") == "active" else "🔴"
        keyboard.add(
            InlineKeyboardButton(
                text=f"{status} {acc.get('phone_masked', 'Unknown')}",
                callback_data=f"accounts:telegram:select:{acc['id']}"
            )
        )
    
    keyboard.add(
        InlineKeyboardButton("➕ إضافة حساب", callback_data="accounts:telegram:add")
    )
    keyboard.add(
        InlineKeyboardButton("🔄 تحديث الحالة", callback_data="accounts:telegram:refresh")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="settings:back")
    )
    return keyboard

def whatsapp_accounts_keyboard(accounts: List[Dict[str, Any]]):
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for acc in accounts:
        status = "🟢" if acc.get("enabled") else "🔴"
        keyboard.add(
            InlineKeyboardButton(
                text=f"{status} {acc.get('name', 'Unknown')}",
                callback_data=f"accounts:whatsapp:select:{acc['id']}"
            )
        )
    
    keyboard.add(
        InlineKeyboardButton("➕ إضافة حساب", callback_data="accounts:whatsapp:add")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="settings:back")
    )
    return keyboard

def whatsapp_select_account_keyboard(accounts: List[Dict[str, Any]]):
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for acc in accounts:
        keyboard.add(
            InlineKeyboardButton(
                text=f"📱 {acc.get('name', 'Unknown')}",
                callback_data=f"whatsapp:select:{acc['id']}"
            )
        )
    
    keyboard.add(
        InlineKeyboardButton("➕ إضافة حساب", callback_data="accounts:whatsapp:add")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="wallet:back")
    )
    return keyboard

def account_action_keyboard(account_id: int, account_type: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    if account_type == "telegram":
        keyboard.add(
            InlineKeyboardButton("🔄 إعادة الاتصال", callback_data=f"accounts:telegram:reconnect:{account_id}")
        )
        keyboard.add(
            InlineKeyboardButton("🗑 حذف", callback_data=f"accounts:telegram:delete:{account_id}")
        )
    elif account_type == "whatsapp":
        keyboard.add(
            InlineKeyboardButton("🔄 تبديل الحالة", callback_data=f"accounts:whatsapp:toggle:{account_id}")
        )
        keyboard.add(
            InlineKeyboardButton("🗑 حذف", callback_data=f"accounts:whatsapp:delete:{account_id}")
        )
    
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=f"accounts:{account_type}:back")
    )
    return keyboard

def account_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("❌ إلغاء", callback_data="accounts:cancel")
    )
    return keyboard
