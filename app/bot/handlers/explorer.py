from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.bot.states.exploration import ExplorationStates
from app.bot.keyboards.explorer import (
    source_confirmation_keyboard,
    source_not_available_keyboard,
    exploration_cancel_keyboard,
    exploration_completed_keyboard,
    results_pagination_keyboard
)
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.userbot import SourceResolver
from app.userbot.manager import UserbotManager
from app.database.database import get_db
from app.database.repositories import (
    TelegramSourceRepository,
    TelegramAccountRepository,
    ScanJobRepository
)
from app.core.enums import AccessStatus, JobStatus, JobType
from app.workers.queue import QueueManager

router = Router()
userbot_manager = UserbotManager()
queue_manager = QueueManager()

@router.callback_query(lambda c: c.data == "explore:start")
async def start_exploration_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "🔍 استكشاف روابط WhatsApp\n\n"
        "أرسل مصدر Telegram الذي تريد استكشافه.\n\n"
        "يمكنك إرسال أحد الخيارات:\n"
        "• @username\n"
        "• رابط المجموعة/القناة\n"
        "• Telegram ID\n"
        "• مصدر تم حفظه مسبقًا\n\n"
        "⚠️ سيتم فحص المصدر الذي تحدده فقط."
    )
    await state.set_state(ExplorationStates.WAITING_SOURCE)

async def start_exploration(message: Message):
    await message.reply(
        "🔍 استكشاف روابط WhatsApp\n\n"
        "أرسل مصدر Telegram الذي تريد استكشافه.\n\n"
        "يمكنك إرسال أحد الخيارات:\n"
        "• @username\n"
        "• رابط المجموعة/القناة\n"
        "• Telegram ID\n"
        "• مصدر تم حفظه مسبقًا"
    )
    await state.set_state(ExplorationStates.WAITING_SOURCE)

@router.message(ExplorationStates.WAITING_SOURCE)
async def process_source(message: Message, state: FSMContext, user_id: int):
    source_input = message.text.strip()
    
    if source_input in ["❌ إلغاء", "🏠 الرئيسية"]:
        await state.clear()
        await message.reply(
            "تم الإلغاء.",
            reply_markup=main_menu_keyboard()
        )
        return

    await state.update_data(source_input=source_input)
    await state.set_state(ExplorationStates.RESOLVING)
    
    resolving_msg = await message.reply("⏳ جاري التحقق من المصدر...")

    async with get_db() as db:
        account_repo = TelegramAccountRepository(db)
        account = account_repo.get_primary_by_user_id(user_id)
        
        if not account:
            await resolving_msg.edit_text(
                "❌ لا يوجد حساب Telegram مرتبط.\n\n"
                "الرجاء إضافة حساب من الإعدادات أولاً."
            )
            await state.clear()
            return

        client = await userbot_manager.get_client(account.id, account.session_encrypted)
        
        parsed = SourceResolver.parse_input(source_input)
        
        if parsed["type"] == "unknown":
            await resolving_msg.edit_text(
                "❌ لم يتم التعرف على المصدر.\n\n"
                "تأكد من إرسال @username, رابط, أو Telegram ID صحيح."
            )
            await state.clear()
            return

        entity, info = await SourceResolver.resolve(client, source_input)
        
        if entity is None or not info:
            await resolving_msg.edit_text(
                "❌ تعذر الوصول إلى المصدر.\n\n"
                "المصدر غير متاح أو غير قابل للوصول حالياً.\n"
                "لم يتم إجراء أي عملية استخراج."
            )
            await state.clear()
            return

        source_repo = TelegramSourceRepository(db)
        source, created = source_repo.get_or_create(
            user_id,
            info["id"],
            username=info.get("username"),
            title=info.get("title"),
            type=info.get("type")
        )
        
        source_repo.update_access_status(source.id, AccessStatus.ACCESSIBLE)
        
        await state.update_data(source_id=source.id)
        await state.set_state(ExplorationStates.READY)
        
        access_status = "🟢 متاح" if info.get("type") != "private" else "🔐 خاص"
        
        await resolving_msg.edit_text(
            f"✅ تم التعرف على المصدر\n\n"
            f"📌 الاسم: {info.get('title') or info.get('username') or 'غير معروف'}\n"
            f"📂 النوع: {info.get('type', 'غير معروف')}\n"
            f"🆔 ID: {info['id']}\n"
            f"🔓 حالة الوصول: {access_status}\n\n"
            f"يمكن بدء الاستكشاف الآن.",
            reply_markup=source_confirmation_keyboard(source.id)
        )

@router.callback_query(lambda c: c.data.startswith("explore:run:"))
async def run_exploration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    source_id = int(callback.data.split(":")[2])
    
    async with get_db() as db:
        scan_job_repo = ScanJobRepository(db)
        
        job_data = {
            "type": JobType.SOURCE_SCAN,
            "user_id": callback.from_user.id,
            "source_id": source_id
        }
        
        job_id = await queue_manager.push(job_data)
        
        scan_job_repo.create(
            id=job_id,
            user_id=callback.from_user.id,
            source_id=source_id,
            type=JobType.SOURCE_SCAN,
            status=JobStatus.PENDING
        )
        
        await state.set_state(ExplorationStates.RUNNING)
        await state.update_data(job_id=job_id)
        
        await callback.message.edit_text(
            f"⏳ بدأ الاستكشاف\n\n"
            f"📂 المصدر: جاري التحميل...\n"
            f"📊 التقدم: 0%\n"
            f"🔗 روابط WhatsApp: 0\n\n"
            f"يرجى الانتظار...",
            reply_markup=exploration_cancel_keyboard(str(job_id))
        )

@router.callback_query(lambda c: c.data == "explore:change")
async def change_source(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await start_exploration_callback(callback, state)

@router.callback_query(lambda c: c.data == "explore:cancel")
async def cancel_exploration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "تم الإلغاء.",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(lambda c: c.data == "explore:retry")
async def retry_exploration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    source_input = data.get("source_input")
    if source_input:
        await state.set_state(ExplorationStates.WAITING_SOURCE)
        await process_source(callback.message, state, callback.from_user.id)

@router.callback_query(lambda c: c.data.startswith("explore:results:"))
async def show_results(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    async with get_db() as db:
        scan_job_repo = ScanJobRepository(db)
        scan_job = scan_job_repo.get(job_id)
        
        if not scan_job:
            await callback.message.edit_text(
                "❌ لم يتم العثور على المهمة.",
                reply_markup=main_menu_keyboard()
            )
            return
        
        total_links = scan_job.total_urls or 0
        whatsapp_links = scan_job.whatsapp_urls or 0
        unique_links = scan_job.unique_urls or 0
        
        await callback.message.edit_text(
            f"🔗 روابط WhatsApp المستخرجة\n\n"
            f"المصدر: {scan_job.source.title if scan_job.source else 'غير معروف'}\n"
            f"إجمالي الروابط الفريدة: {unique_links}\n\n"
            f"الصفحة 1 / {max(1, (unique_links + 19) // 20)}",
            reply_markup=results_pagination_keyboard(job_id, 1, max(1, (unique_links + 19) // 20))
        )