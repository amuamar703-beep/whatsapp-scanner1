from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any

def telegram_accounts_keyboard(accounts: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for acc in accounts:
        status = "🟢" if acc.get("status") == "active" else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {acc.get('phone_masked', 'Unknown')}",
                callback_data=f"accounts:telegram:select:{acc['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ إضافة حساب", callback_data="accounts:telegram:add")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 تحديث الحالة", callback_data="accounts:telegram:refresh")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="settings:back")
    )
    return builder.as_markup()

def whatsapp_accounts_keyboard(accounts: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for acc in accounts:
        status = "🟢" if acc.get("enabled") else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {acc.get('name', 'Unknown')}",
                callback_data=f"accounts:whatsapp:select:{acc['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ إضافة حساب", callback_data="accounts:whatsapp:add")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="settings:back")
    )
    return builder.as_markup()

def whatsapp_select_account_keyboard(accounts: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for acc in accounts:
        builder.row(
            InlineKeyboardButton(
                text=f"📱 {acc.get('name', 'Unknown')}",
                callback_data=f"whatsapp:select:{acc['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ إضافة حساب", callback_data="accounts:whatsapp:add")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="wallet:back")
    )
    return builder.as_markup()

def account_action_keyboard(account_id: int, account_type: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if account_type == "telegram":
        builder.row(
            InlineKeyboardButton(text="🔄 إعادة الاتصال", callback_data=f"accounts:telegram:reconnect:{account_id}")
        )
        builder.row(
            InlineKeyboardButton(text="🗑 حذف", callback_data=f"accounts:telegram:delete:{account_id}")
        )
    elif account_type == "whatsapp":
        builder.row(
            InlineKeyboardButton(text="🔄 تبديل الحالة", callback_data=f"accounts:whatsapp:toggle:{account_id}")
        )
        builder.row(
            InlineKeyboardButton(text="🗑 حذف", callback_data=f"accounts:whatsapp:delete:{account_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"accounts:{account_type}:back")
    )
    return builder.as_markup()

def account_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ إلغاء", callback_data="accounts:cancel")
    )
    return builder.as_markup()