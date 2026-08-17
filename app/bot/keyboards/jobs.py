from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def jobs_keyboard(jobs: list):
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for job in jobs:
        status_icon = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫"
        }.get(job.get("status", "unknown"), "❓")
        
        keyboard.add(
            InlineKeyboardButton(
                text=f"{status_icon} {job.get('type', 'Unknown')} #{str(job.get('id'))[:8]}",
                callback_data=f"jobs:view:{job['id']}"
            )
        )
    
    keyboard.add(
        InlineKeyboardButton("🔄 تحديث", callback_data="jobs:refresh")
    )
    keyboard.add(
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu:back")
    )
    return keyboard

def job_detail_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔄 تحديث الحالة", callback_data=f"jobs:refresh:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("❌ إلغاء المهمة", callback_data=f"jobs:cancel:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="jobs:back")
    )
    return keyboard

def job_cancel_confirm_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ إلغاء", callback_data=f"jobs:confirm_cancel:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("❌ متابعة", callback_data=f"jobs:view:{job_id}")
    )
    return keyboard
