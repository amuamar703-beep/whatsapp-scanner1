from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.keyboards.wallet import wallet_category_keyboard
from app.bot.keyboards.wallet_send import wallet_send_whatsapp_keyboard
from app.bot.keyboards.accounts import whatsapp_select_account_keyboard
from app.services.accounts import AccountsService
from app.services.wallet import WalletService
from app.core.enums import WalletCategory

router = Router()
accounts_service = AccountsService()
wallet_service = WalletService()

@router.callback_query(lambda c: c.data.startswith("wallet:send:"))
async def wallet_send_whatsapp(callback: CallbackQuery, user_id: int):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    await callback.message.edit_text(
        "📱 إرسال إلى WhatsApp\n\n"
        "اختر الفئة للإرسال:",
        reply_markup=wallet_category_keyboard("send")
    )

@router.callback_query(lambda c: c.data.startswith("wallet:send_category:"))
async def wallet_send_category(callback: CallbackQuery, user_id: int):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    accounts_result = await accounts_service.get_whatsapp_accounts_for_send(user_id)
    
    if not accounts_result["success"] or accounts_result["total"] == 0:
        await callback.message.edit_text(
            "📱 إرسال إلى WhatsApp\n\n"
            "لا توجد حسابات WhatsApp نشطة.\n"
            "الرجاء إضافة حساب من الإعدادات أولاً.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    wallet_result = await wallet_service.get_wallet_links(
        user_id,
        wallet_category,
        page=1,
        per_page=50
    )
    
    if not wallet_result["success"] or wallet_result["total"] == 0:
        await callback.message.edit_text(
            f"📱 إرسال إلى WhatsApp\n\n"
            f"لا توجد روابط في فئة '{category}'.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    text = (
        f"📱 إرسال إلى WhatsApp\n\n"
        f"📂 الفئة: {'🟢 مباشر' if category == 'direct_join' else '🟡 طلب'}\n"
        f"📦 عدد الروابط: {wallet_result['total']}\n\n"
        f"اختر الحساب:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=whatsapp_select_account_keyboard(accounts_result["accounts"])
    )

@router.callback_query(lambda c: c.data.startswith("whatsapp:select:"))
async def whatsapp_select_account(callback: CallbackQuery, user_id: int):
    await callback.answer()
    account_id = int(callback.data.split(":")[2])
    
    accounts_result = await accounts_service.get_whatsapp_accounts(user_id)
    
    if not accounts_result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ",
            reply_markup=main_menu_keyboard()
        )
        return
    
    selected = None
    for acc in accounts_result["accounts"]:
        if acc["id"] == account_id:
            selected = acc
            break
    
    if not selected:
        await callback.answer("الحساب غير موجود")
        return
    
    if not selected.get("direct_url"):
        await callback.message.edit_text(
            f"📱 {selected['name']}\n\n"
            "❌ لا يوجد رابط مباشر لهذا الحساب.\n"
            "الرجاء تحديث الحساب من الإعدادات.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    category = None
    data = await state.get_data()
    category = data.get("send_category")
    
    if not category:
        await callback.answer("فئة غير محددة")
        return
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    wallet_result = await wallet_service.get_wallet_links(
        user_id,
        wallet_category
    )
    
    if not wallet_result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ في جلب الروابط",
            reply_markup=main_menu_keyboard()
        )
        return
    
    links = [link["url"] for link in wallet_result["links"]]
    
    if not links:
        await callback.message.edit_text(
            "لا توجد روابط للإرسال.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    links_text = "\n".join(links[:10])
    if len(links) > 10:
        links_text += f"\n... و {len(links) - 10} رابط آخر"
    
    text = (
        f"📱 إرسال إلى WhatsApp\n\n"
        f"📂 الفئة: {'🟢 مباشر' if category == 'direct_join' else '🟡 طلب'}\n"
        f"📦 عدد الروابط: {len(links)}\n"
        f"📱 الحساب: {selected['name']}\n\n"
        f"🔗 الروابط:\n{links_text}\n\n"
        f"اضغط على الزر أدناه لفتح WhatsApp:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=wallet_send_whatsapp_keyboard(selected["direct_url"], links, category)
    )

@router.callback_query(lambda c: c.data.startswith("whatsapp:copy:"))
async def whatsapp_copy_links(callback: CallbackQuery, user_id: int):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    wallet_result = await wallet_service.get_wallet_links(
        user_id,
        wallet_category
    )
    
    if not wallet_result["success"]:
        await callback.answer("حدث خطأ")
        return
    
    links = [link["url"] for link in wallet_result["links"]]
    links_text = "\n".join(links)
    
    await callback.message.answer(
        f"📋 تم نسخ {len(links)} رابط:\n\n{links_text[:4000]}"
    )