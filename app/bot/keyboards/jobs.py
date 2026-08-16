from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def jobs_keyboard(jobs: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for job in jobs:
        status_icon = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫"
        }.get(job.get("status", "unknown"), "❓")
        
        builder.row(
            InlineKeyboardButton(
                text=f"{status_icon} {job.get('type', 'Unknown')} #{str(job.get('id'))[:8]}",
                callback_data=f"jobs:view:{job['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔄 تحديث", callback_data="jobs:refresh")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu:back")
    )
    return builder.as_markup()

def job_detail_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔄 تحديث الحالة", callback_data=f"jobs:refresh:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ إلغاء المهمة", callback_data=f"jobs:cancel:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="jobs:back")
    )
    return builder.as_markup()

def job_cancel_confirm_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ إلغاء", callback_data=f"jobs:confirm_cancel:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ متابعة", callback_data=f"jobs:view:{job_id}")
    )
    return builder.as_markup()