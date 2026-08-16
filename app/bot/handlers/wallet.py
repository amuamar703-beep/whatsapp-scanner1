from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states.wallet import WalletStates
from app.bot.keyboards.wallet import (
    wallet_main_keyboard,
    wallet_category_keyboard,
    wallet_pagination_keyboard,
    wallet_confirm_delete_keyboard,
    wallet_confirm_save_keyboard
)
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.keyboards.export import export_wallet_format_keyboard
from app.services.wallet import WalletService
from app.services.export import ExportService
from app.services.accounts import AccountsService
from app.core.enums import WalletCategory, ExportFormat

router = Router()
wallet_service = WalletService()
export_service = ExportService()
accounts_service = AccountsService()

@router.callback_query(lambda c: c.data == "wallet:open")
async def open_wallet(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    await state.set_state(WalletStates.MAIN)
    
    stats = await wallet_service.get_wallet_stats(user_id)
    
    if not stats["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ في جلب إحصائيات المحفظة",
            reply_markup=main_menu_keyboard()
        )
        return
    
    text = (
        "💼 محفظتي\n\n"
        f"📊 إجمالي الروابط المحفوظة: {stats['stats']['total']}\n"
        f"🟢 الانضمام المباشر: {stats['stats']['direct_join']}\n"
        f"🟡 طلب الانضمام: {stats['stats']['request_join']}\n\n"
        "اختر القسم:"
    )
    
    await callback.message.edit_text(text, reply_markup=wallet_main_keyboard())

@router.callback_query(lambda c: c.data == "wallet:direct")
async def wallet_direct_links(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    await state.set_state(WalletStates.DIRECT)
    
    result = await wallet_service.get_wallet_links(
        user_id,
        WalletCategory.DIRECT_JOIN,
        page=1
    )
    
    if not result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ في جلب الروابط",
            reply_markup=wallet_main_keyboard()
        )
        return
    
    if result["total"] == 0:
        await callback.message.edit_text(
            "💼 محفظتي\n\n🟢 الانضمام المباشر\n\nلا توجد روابط في هذه الفئة.",
            reply_markup=wallet_category_keyboard("direct")
        )
        return
    
    links_text = "\n".join([
        f"{i+1}. {link['url'][:50]}"
        for i, link in enumerate(result["links"])
    ])
    
    text = (
        f"💼 محفظتي\n\n"
        f"🟢 الانضمام المباشر\n"
        f"عدد الروابط: {result['total']}\n\n"
        f"{links_text}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=wallet_pagination_keyboard("direct", result["page"], result["total_pages"])
    )

@router.callback_query(lambda c: c.data == "wallet:request")
async def wallet_request_links(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    await state.set_state(WalletStates.REQUEST)
    
    result = await wallet_service.get_wallet_links(
        user_id,
        WalletCategory.REQUEST_JOIN,
        page=1
    )
    
    if not result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ في جلب الروابط",
            reply_markup=wallet_main_keyboard()
        )
        return
    
    if result["total"] == 0:
        await callback.message.edit_text(
            "💼 محفظتي\n\n🟡 طلب الانضمام\n\nلا توجد روابط في هذه الفئة.",
            reply_markup=wallet_category_keyboard("request")
        )
        return
    
    links_text = "\n".join([
        f"{i+1}. {link['url'][:50]}"
        for i, link in enumerate(result["links"])
    ])
    
    text = (
        f"💼 محفظتي\n\n"
        f"🟡 طلب الانضمام\n"
        f"عدد الروابط: {result['total']}\n\n"
        f"{links_text}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=wallet_pagination_keyboard("request", result["page"], result["total_pages"])
    )

@router.callback_query(lambda c: c.data.startswith("wallet:page:"))
async def wallet_page(callback: CallbackQuery, user_id: int):
    await callback.answer()
    parts = callback.data.split(":")
    category = parts[2]
    page = int(parts[3])
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    result = await wallet_service.get_wallet_links(
        user_id,
        wallet_category,
        page=page
    )
    
    if not result["success"]:
        await callback.answer("حدث خطأ")
        return
    
    links_text = "\n".join([
        f"{i+1}. {link['url'][:50]}"
        for i, link in enumerate(result["links"])
    ])
    
    category_name = "🟢 الانضمام المباشر" if category == "direct_join" else "🟡 طلب الانضمام"
    
    text = (
        f"💼 محفظتي\n\n"
        f"{category_name}\n"
        f"عدد الروابط: {result['total']}\n\n"
        f"{links_text}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=wallet_pagination_keyboard(category, result["page"], result["total_pages"])
    )

@router.callback_query(lambda c: c.data == "wallet:stats")
async def wallet_stats(callback: CallbackQuery, user_id: int):
    await callback.answer()
    
    stats = await wallet_service.get_wallet_stats(user_id)
    
    if not stats["success"]:
        await callback.answer("حدث خطأ")
        return
    
    text = (
        "📊 إحصائيات المحفظة\n\n"
        f"📦 إجمالي الروابط: {stats['stats']['total']}\n"
        f"🟢 الانضمام المباشر: {stats['stats']['direct_join']}\n"
        f"🟡 طلب الانضمام: {stats['stats']['request_join']}"
    )
    
    await callback.message.edit_text(text, reply_markup=wallet_main_keyboard())

@router.callback_query(lambda c: c.data == "wallet:manage")
async def wallet_manage(callback: CallbackQuery):
    await callback.answer()
    
    text = (
        "🗑 إدارة المحفوظات\n\n"
        "اختر الفئة التي تريد إدارتها:"
    )
    
    await callback.message.edit_text(text, reply_markup=wallet_main_keyboard())

@router.callback_query(lambda c: c.data.startswith("wallet:delete:"))
async def wallet_delete_confirm(callback: CallbackQuery):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    text = (
        f"🗑 حذف الروابط\n\n"
        f"هل تريد حذف جميع روابط '{category}' من المحفظة؟\n\n"
        f"⚠️ هذا الإجراء لا يمكن التراجع عنه."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=wallet_confirm_delete_keyboard(category)
    )

@router.callback_query(lambda c: c.data.startswith("wallet:confirm_delete:"))
async def wallet_confirm_delete(callback: CallbackQuery, user_id: int):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    result = await wallet_service.get_wallet_links(user_id, wallet_category)
    
    if not result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ",
            reply_markup=wallet_main_keyboard()
        )
        return
    
    link_ids = [link["link_id"] for link in result["links"]]
    
    delete_result = await wallet_service.remove_from_wallet_by_link(user_id, link_ids)
    
    await callback.message.edit_text(
        f"✅ تم حذف {delete_result['deleted']} رابط بنجاح.",
        reply_markup=wallet_main_keyboard()
    )

@router.callback_query(lambda c: c.data == "wallet:back")
async def wallet_back(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    await state.set_state(WalletStates.MAIN)
    await open_wallet(callback, state, user_id)

@router.callback_query(lambda c: c.data.startswith("wallet:save:"))
async def wallet_save_confirm(callback: CallbackQuery, user_id: int):
    await callback.answer()
    parts = callback.data.split(":")
    job_id = parts[2]
    category = parts[3]
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    from app.services.analysis import AnalysisService
    analysis_service = AnalysisService()
    
    result = await analysis_service.get_analysis_results(job_id, category)
    
    if not result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ",
            reply_markup=main_menu_keyboard()
        )
        return
    
    links = result["results"]["links"]
    
    if not links:
        await callback.message.edit_text(
            "لا توجد روابط لحفظها.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    link_ids = [link["id"] for link in links]
    
    text = (
        f"💾 حفظ الروابط\n\n"
        f"سيتم حفظ: {len(link_ids)} رابطاً\n"
        f"ضمن: {'🟢 الانضمام المباشر' if category == 'direct_join' else '🟡 طلب الانضمام'}\n\n"
        f"هل تريد المتابعة؟"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=wallet_confirm_save_keyboard(job_id, category)
    )

@router.callback_query(lambda c: c.data.startswith("wallet:confirm_save:"))
async def wallet_confirm_save(callback: CallbackQuery, user_id: int):
    await callback.answer()
    parts = callback.data.split(":")
    job_id = parts[2]
    category = parts[3]
    
    try:
        wallet_category = WalletCategory(category)
    except ValueError:
        await callback.answer("فئة غير صالحة")
        return
    
    from app.services.analysis import AnalysisService
    analysis_service = AnalysisService()
    
    result = await analysis_service.get_analysis_results(job_id, category)
    
    if not result["success"]:
        await callback.message.edit_text(
            "❌ حدث خطأ",
            reply_markup=main_menu_keyboard()
        )
        return
    
    links = result["results"]["links"]
    link_ids = [link["id"] for link in links]
    
    save_result = await wallet_service.add_to_wallet(user_id, link_ids, wallet_category)
    
    await callback.message.edit_text(
        f"✅ تم الحفظ بنجاح\n\n"
        f"تمت إضافة: {save_result['added']} رابطاً\n"
        f"إلى: 💼 محفظتي ← {'🟢 الانضمام المباشر' if category == 'direct_join' else '🟡 طلب الانضمام'}",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith("wallet:send:"))
async def wallet_send_whatsapp(callback: CallbackQuery, user_id: int):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    accounts_result = await accounts_service.get_whatsapp_accounts_for_send(user_id)
    
    if not accounts_result["success"] or accounts_result["total"] == 0:
        await callback.message.edit_text(
            "📱 إرسال إلى WhatsApp\n\n"
            "لا توجد حسابات WhatsApp.\n"
            "الرجاء إضافة حساب من الإعدادات أولاً.",
            reply_markup=wallet_category_keyboard(category)
        )
        return
    
    from app.bot.keyboards.accounts import whatsapp_select_account_keyboard
    
    text = (
        "📱 إرسال إلى WhatsApp\n\n"
        "اختر الحساب الذي تريد استخدامه:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=whatsapp_select_account_keyboard(accounts_result["accounts"])
    )