from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def wallet_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 الانضمام المباشر", callback_data="wallet:direct")
    )
    builder.row(
        InlineKeyboardButton(text="🟡 طلب الانضمام", callback_data="wallet:request")
    )
    builder.row(
        InlineKeyboardButton(text="📊 إحصائيات المحفظة", callback_data="wallet:stats")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 إدارة المحفوظات", callback_data="wallet:manage")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu:back")
    )
    return builder.as_markup()

def wallet_category_keyboard(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📤 تصدير", callback_data=f"export:wallet:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="📱 إرسال إلى WhatsApp", callback_data=f"wallet:send:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 حذف الروابط", callback_data=f"wallet:delete:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="wallet:back")
    )
    return builder.as_markup()

def wallet_pagination_keyboard(
    category: str,
    current_page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"wallet:page:{category}:{current_page - 1}"
            )
        )
    
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page} / {total_pages}",
            callback_data="ignore"
        )
    )
    
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"wallet:page:{category}:{current_page + 1}"
            )
        )
    
    builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(text="📤 تصدير", callback_data=f"export:wallet:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data="wallet:back")
    )
    return builder.as_markup()

def wallet_confirm_delete_keyboard(category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ نعم، حذف", callback_data=f"wallet:confirm_delete:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ إلغاء", callback_data=f"wallet:back")
    )
    return builder.as_markup()

def wallet_confirm_save_keyboard(job_id: str, category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ حفظ", callback_data=f"wallet:confirm_save:{job_id}:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ إلغاء", callback_data=f"analysis:back:{job_id}")
    )
    return builder.as_markup()