from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def source_confirmation_keyboard(source_id: int):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚀 بدء الاستكشاف", callback_data=f"explore:run:{source_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🔄 تغيير المصدر", callback_data="explore:change"),
        InlineKeyboardButton("❌ إلغاء", callback_data="explore:cancel")
    )
    return keyboard

def source_not_available_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 المحاولة مرة أخرى", callback_data="explore:retry"),
        InlineKeyboardButton("📍 مصدر آخر", callback_data="explore:change")
    )
    keyboard.add(
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu:back")
    )
    return keyboard

def exploration_cancel_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⏸ إيقاف مؤقت", callback_data=f"job:pause:{job_id}"),
        InlineKeyboardButton("🛑 إلغاء", callback_data=f"job:cancel:{job_id}")
    )
    return keyboard

def exploration_completed_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📋 عرض روابط WhatsApp", callback_data=f"explore:results:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🔍 بدء الفحص", callback_data=f"analysis:start:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("📊 تفاصيل الاستكشاف", callback_data=f"explore:details:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu:back")
    )
    return keyboard

def results_pagination_keyboard(job_id: str, current_page: int, total_pages: int):
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️", callback_data=f"links:page:{job_id}:{current_page - 1}")
        )
    
    nav_buttons.append(
        InlineKeyboardButton(f"{current_page} / {total_pages}", callback_data="ignore")
    )
    
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("▶️", callback_data=f"links:page:{job_id}:{current_page + 1}")
        )
    
    keyboard.add(*nav_buttons)
    keyboard.add(
        InlineKeyboardButton("🔍 بدء فحص الروابط", callback_data=f"analysis:start:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=f"explore:back:{job_id}")
    )
    return keyboard
