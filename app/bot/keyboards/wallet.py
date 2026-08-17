from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def wallet_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🟢 الانضمام المباشر", callback_data="wallet:direct")
    )
    keyboard.add(
        InlineKeyboardButton("🟡 طلب الانضمام", callback_data="wallet:request")
    )
    keyboard.add(
        InlineKeyboardButton("📊 إحصائيات المحفظة", callback_data="wallet:stats")
    )
    keyboard.add(
        InlineKeyboardButton("🗑 إدارة المحفوظات", callback_data="wallet:manage")
    )
    keyboard.add(
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu:back")
    )
    return keyboard

def wallet_category_keyboard(category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📤 تصدير", callback_data=f"export:wallet:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("📱 إرسال إلى WhatsApp", callback_data=f"wallet:send:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("🗑 حذف الروابط", callback_data=f"wallet:delete:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="wallet:back")
    )
    return keyboard

def wallet_pagination_keyboard(category: str, current_page: int, total_pages: int):
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️", callback_data=f"wallet:page:{category}:{current_page - 1}")
        )
    
    nav_buttons.append(
        InlineKeyboardButton(f"{current_page} / {total_pages}", callback_data="ignore")
    )
    
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("▶️", callback_data=f"wallet:page:{category}:{current_page + 1}")
        )
    
    keyboard.add(*nav_buttons)
    keyboard.add(
        InlineKeyboardButton("📤 تصدير", callback_data=f"export:wallet:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="wallet:back")
    )
    return keyboard

def wallet_confirm_delete_keyboard(category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ نعم، حذف", callback_data=f"wallet:confirm_delete:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("❌ إلغاء", callback_data="wallet:back")
    )
    return keyboard

def wallet_confirm_save_keyboard(job_id: str, category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ حفظ", callback_data=f"wallet:confirm_save:{job_id}:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("❌ إلغاء", callback_data=f"analysis:back:{job_id}")
    )
    return keyboard

def wallet_send_whatsapp_keyboard(direct_url: str, links: list, category: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📱 فتح WhatsApp", url=direct_url)
    )
    keyboard.add(
        InlineKeyboardButton("📋 نسخ الروابط", callback_data=f"whatsapp:copy:{category}")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="wallet:back")
    )
    return keyboard
