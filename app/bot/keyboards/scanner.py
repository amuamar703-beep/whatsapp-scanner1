from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def analysis_confirmation_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 نعم، ابدأ الفحص", callback_data=f"analysis:confirm:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ إلغاء", callback_data=f"analysis:cancel:{job_id}")
    )
    return builder.as_markup()

def analysis_results_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟢 الانضمام المباشر", callback_data=f"analysis:direct:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🟡 طلب الانضمام", callback_data=f"analysis:request:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔴 غير صالحة", callback_data=f"analysis:invalid:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⚪ حالات أخرى", callback_data=f"analysis:other:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 الرئيسية", callback_data="main_menu:back")
    )
    return builder.as_markup()

def category_actions_keyboard(job_id: str, category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💾 حفظ في محفظتي", callback_data=f"wallet:save:{job_id}:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="📤 تصدير", callback_data=f"export:start:{job_id}:{category}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return builder.as_markup()

def invalid_links_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🗑 استبعاد من النتائج", callback_data=f"analysis:exclude:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 إعادة الفحص", callback_data=f"analysis:rescan:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return builder.as_markup()

def other_links_keyboard(job_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 إعادة الفحص", callback_data=f"analysis:rescan:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📋 عرض الروابط", callback_data=f"analysis:view_other:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 استبعاد", callback_data=f"analysis:exclude:{job_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"analysis:back:{job_id}")
    )
    return builder.as_markup()