from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def settings_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📱 حسابات WhatsApp", callback_data="settings:whatsapp")
    )
    keyboard.add(
        InlineKeyboardButton("👤 حساب Telegram", callback_data="settings:telegram")
    )
    keyboard.add(
        InlineKeyboardButton("📊 إعدادات الاستكشاف", callback_data="settings:exploration")
    )
    keyboard.add(
        InlineKeyboardButton("🔔 الإشعارات", callback_data="settings:notifications")
    )
    keyboard.add(
        InlineKeyboardButton("🌐 اللغة", callback_data="settings:language")
    )
    keyboard.add(
        InlineKeyboardButton("🧹 إدارة البيانات", callback_data="settings:data")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu:back")
    )
    return keyboard

def exploration_settings_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📄 عدد الروابط في الصفحة: 20", callback_data="settings:per_page")
    )
    keyboard.add(
        InlineKeyboardButton("📅 نطاق الاستكشاف: كل الرسائل", callback_data="settings:scope")
    )
    keyboard.add(
        InlineKeyboardButton("⚡ الفحص التلقائي: ❌ متوقف", callback_data="settings:auto_scan")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="settings:back")
    )
    return keyboard

def data_management_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🗑 مسح المهام المكتملة", callback_data="settings:clear_jobs")
    )
    keyboard.add(
        InlineKeyboardButton("🗑 مسح سجل العمليات", callback_data="settings:clear_logs")
    )
    keyboard.add(
        InlineKeyboardButton("🗑 مسح جميع البيانات", callback_data="settings:clear_all")
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ رجوع", callback_data="settings:back")
    )
    return keyboard
