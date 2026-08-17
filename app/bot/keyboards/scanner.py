from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def analysis_confirmation_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🚀 نعم، ابدأ الفحص", callback_data=f"analysis:confirm:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("❌ إلغاء", callback_data=f"analysis:cancel:{job_id}")
    )
    return keyboard

def analysis_results_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🟢 الانضمام المباشر", callback_data=f"analysis:direct:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🟡 طلب الانضمام", callback_data=f"analysis:request:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🔴 غير صالحة", callback_data=f"analysis:invalid:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("⚪ حالات أخرى", callback_data=f"analysis:other:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu:back")
    )
    return keyboard

def category_actions_keyboard(job_id: str, category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💾 حفظ في محفظتي", callback_data=f"wallet:save:{job_id}:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("📤 تصدير", callback_data=f"export:start:{job_id}:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return keyboard

def invalid_links_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🗑 استبعاد من النتائج", callback_data=f"analysis:exclude:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🔄 إعادة الفحص", callback_data=f"analysis:rescan:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return keyboard

def other_links_keyboard(job_id: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔄 إعادة الفحص", callback_data=f"analysis:rescan:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("📋 عرض الروابط", callback_data=f"analysis:view_other:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("🗑 استبعاد", callback_data=f"analysis:exclude:{job_id}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return keyboard
