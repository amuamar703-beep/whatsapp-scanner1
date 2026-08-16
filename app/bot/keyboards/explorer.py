from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def source_confirmation_keyboard(source_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 بدء الاستكشاف", callback_data=f"explore:run:{source_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 تغيير المصدر", callback_data="explore:change"),
        InlineKeyboardButton(text="❌ إلغاء", callback_data="explore:cancel")
    )
    return builder.as_markup()

def source_not_available_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 المحاولة مرة أخرى", callback_data="explore:retry"),
        InlineKeyboardButton(text="📍 مصدر آخر", callback_data="explore:change")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu:back")
    )
    return builder.as_markup()

def exploration_cancel_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏸ إيقاف مؤقت", callback_data=f"job:pause:{job_id}"),
        InlineKeyboardButton(text="🛑 إلغاء", callback_data=f"job:cancel:{job_id}")
    )
    return builder.as_markup()

def exploration_completed_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 عرض روابط WhatsApp", callback_data=f"explore:results:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 بدء الفحص", callback_data=f"analysis:start:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📊 تفاصيل الاستكشاف", callback_data=f"explore:details:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu:back")
    )
    return builder.as_markup()

def results_pagination_keyboard(
    job_id: str,
    current_page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"links:page:{job_id}:{current_page - 1}"
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
                callback_data=f"links:page:{job_id}:{current_page + 1}"
            )
        )
    
    builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(text="🔍 بدء فحص الروابط", callback_data=f"analysis:start:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"explore:back:{job_id}")
    )
    return builder.as_markup()