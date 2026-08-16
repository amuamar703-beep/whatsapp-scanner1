from aiogram import Router
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from app.bot.states.export import ExportStates
from app.bot.keyboards.export import export_format_keyboard, export_wallet_format_keyboard
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.keyboards.wallet import wallet_main_keyboard
from app.services.export import ExportService
from app.services.wallet import WalletService
from app.core.enums import ExportFormat, WalletCategory

router = Router()
export_service = ExportService()
wallet_service = WalletService()

@router.callback_query(lambda c: c.data.startswith("export:start:"))
async def export_select_format(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split(":")
    job_id = parts[2]
    category = parts[3]
    
    await state.update_data(job_id=job_id, category=category)
    await state.set_state(ExportStates.SELECT_FORMAT)
    
    text = (
        "📤 تصدير الروابط\n\n"
        "اختر صيغة التصدير:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=export_format_keyboard(job_id, category)
    )

@router.callback_query(lambda c: c.data.startswith("export:format:"))
async def export_generate(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    parts = callback.data.split(":")
    job_id = parts[2]
    format_type = parts[3]
    category = parts[4]
    
    await state.set_state(ExportStates.GENERATING)
    await callback.message.edit_text("⏳ جاري إنشاء ملف التصدير...")
    
    try:
        format_enum = ExportFormat(format_type)
        category_enum = WalletCategory(category)
    except ValueError:
        await callback.message.edit_text(
            "❌ صيغة أو فئة غير صالحة",
            reply_markup=main_menu_keyboard()
        )
        return
    
    result = await export_service.start_export(
        user_id,
        format_enum,
        category_enum
    )
    
    if not result["success"]:
        await callback.message.edit_text(
            f"❌ حدث خطأ: {result.get('error', 'غير معروف')}",
            reply_markup=main_menu_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"✅ تم بدء عملية التصدير\n\n"
        f"📄 الصيغة: {format_type.upper()}\n"
        f"📂 الفئة: {category}\n"
        f"🆔 رقم المهمة: {result['job_id'][:8]}...\n\n"
        f"سيتم إشعارك عند الانتهاء.",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith("export:wallet:"))
async def export_wallet_select_format(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split(":")[2]
    
    await state.update_data(category=category)
    await state.set_state(ExportStates.SELECT_FORMAT)
    
    text = (
        "📤 تصدير روابط المحفظة\n\n"
        "اختر صيغة التصدير:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=export_wallet_format_keyboard(category)
    )

@router.callback_query(lambda c: c.data.startswith("export:wallet_format:"))
async def export_wallet_generate(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    parts = callback.data.split(":")
    category = parts[2]
    format_type = parts[3]
    
    await state.set_state(ExportStates.GENERATING)
    await callback.message.edit_text("⏳ جاري إنشاء ملف التصدير...")
    
    try:
        format_enum = ExportFormat(format_type)
        category_enum = WalletCategory(category)
    except ValueError:
        await callback.message.edit_text(
            "❌ صيغة أو فئة غير صالحة",
            reply_markup=wallet_main_keyboard()
        )
        return
    
    result = await export_service.generate_export_content(
        user_id,
        category_enum,
        format_enum
    )
    
    if not result["success"]:
        await callback.message.edit_text(
            f"❌ حدث خطأ: {result.get('error', 'غير معروف')}",
            reply_markup=wallet_main_keyboard()
        )
        return
    
    file = FSInputFile(result["file_path"])
    
    await callback.message.delete()
    
    await callback.message.answer_document(
        document=file,
        caption=(
            f"📤 تم التصدير بنجاح\n\n"
            f"📄 الصيغة: {format_type.upper()}\n"
            f"📂 الفئة: {category}\n"
            f"📦 عدد الروابط: {result['total_links']}"
        ),
        reply_markup=wallet_main_keyboard()
    )

@router.callback_query(lambda c: c.data.startswith("export:view:"))
async def export_view(callback: CallbackQuery, user_id: int):
    await callback.answer()
    export_id = callback.data.split(":")[2]
    
    result = await export_service.get_export_file(user_id, export_id)
    
    if not result["success"]:
        await callback.message.edit_text(
            f"❌ {result.get('error', 'حدث خطأ')}",
            reply_markup=main_menu_keyboard()
        )
        return
    
    file = FSInputFile(result["file_path"])
    
    await callback.message.answer_document(
        document=file,
        caption=(
            f"📤 ملف التصدير\n\n"
            f"📄 الصيغة: {result['format'].upper()}\n"
            f"📦 عدد الروابط: {result['total_links']}\n"
            f"📅 تاريخ الإنشاء: {result['created_at']}"
        )
    )

@router.callback_query(lambda c: c.data.startswith("export:delete:"))
async def export_delete(callback: CallbackQuery, user_id: int):
    await callback.answer()
    export_id = callback.data.split(":")[2]
    
    result = await export_service.delete_export(user_id, export_id)
    
    if not result["success"]:
        await callback.answer(result.get("error", "حدث خطأ"), show_alert=True)
        return
    
    await callback.answer("تم حذف الملف بنجاح")

@router.message(lambda message: message.text == "📤 تصدير" or message.text == "Export")
async def export_wallet(message: Message, state: FSMContext, user_id: int):
    await state.set_state(ExportStates.SELECT_FORMAT)
    
    text = (
        "📤 تصدير روابط المحفظة\n\n"
        "اختر الفئة للتصدير:"
    )
    
    await message.reply(text, reply_markup=wallet_main_keyboard())