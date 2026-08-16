from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.states.analysis import AnalysisStates
from app.bot.keyboards.scanner import (
    analysis_confirmation_keyboard,
    analysis_results_keyboard,
    category_actions_keyboard,
    invalid_links_keyboard,
    other_links_keyboard
)
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.database.database import get_db
from app.database.repositories import ScanJobRepository, WhatsAppLinkRepository
from app.core.enums import JobStatus, JobType, LinkStatus
from app.workers.queue import QueueManager

router = Router()
queue_manager = QueueManager()

@router.callback_query(lambda c: c.data.startswith("analysis:start:"))
async def start_analysis(callback: CallbackQuery, state: FSMContext):
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
        
        total_links = scan_job.whatsapp_urls or 0
        
        await callback.message.edit_text(
            f"🔍 فحص روابط WhatsApp\n\n"
            f"سيتم فحص: {total_links} رابطاً\n"
            f"وسيتم تصنيفها حسب حالتها.\n\n"
            f"هل تريد بدء الفحص؟",
            reply_markup=analysis_confirmation_keyboard(job_id)
        )

@router.callback_query(lambda c: c.data.startswith("analysis:confirm:"))
async def confirm_analysis(callback: CallbackQuery, state: FSMContext):
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
        
        job_data = {
            "type": JobType.LINK_ANALYSIS,
            "user_id": scan_job.user_id,
            "source_id": scan_job.source_id
        }
        
        analysis_job_id = await queue_manager.push(job_data)
        
        scan_job_repo.update(
            analysis_job_id,
            user_id=scan_job.user_id,
            source_id=scan_job.source_id,
            type=JobType.LINK_ANALYSIS,
            status=JobStatus.RUNNING
        )
        
        await state.set_state(AnalysisStates.RUNNING)
        await state.update_data(analysis_job_id=analysis_job_id)
        
        await callback.message.edit_text(
            "🔍 جاري فحص الروابط\n"
            "████████░░░░ 0%\n\n"
            f"📊 الإجمالي: {scan_job.whatsapp_urls or 0}\n"
            "✅ تم الفحص: 0\n"
            "🟢 انضمام مباشر: 0\n"
            "🟡 طلب انضمام: 0\n"
            "🔴 غير صالحة: 0\n"
            "⚪ حالات أخرى: 0",
            reply_markup=None
        )

@router.callback_query(lambda c: c.data.startswith("analysis:direct:"))
async def show_direct_links(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    async with get_db() as db:
        link_repo = WhatsAppLinkRepository(db)
        
        links = link_repo.get_by_status(LinkStatus.DIRECT_JOIN)
        
        if not links:
            await callback.message.edit_text(
                "🟢 روابط الانضمام المباشر\n\n"
                "لا توجد روابط في هذه الفئة.",
                reply_markup=category_actions_keyboard(job_id, "direct")
            )
            return
        
        links_text = "\n".join([
            f"{i+1}. {link.display_url or link.normalized_url[:50]}"
            for i, link in enumerate(links[:20])
        ])
        
        await callback.message.edit_text(
            f"🟢 روابط الانضمام المباشر\n\n"
            f"عدد الروابط: {len(links)}\n\n"
            f"{links_text}",
            reply_markup=category_actions_keyboard(job_id, "direct")
        )

@router.callback_query(lambda c: c.data.startswith("analysis:request:"))
async def show_request_links(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    async with get_db() as db:
        link_repo = WhatsAppLinkRepository(db)
        
        links = link_repo.get_by_status(LinkStatus.REQUEST_JOIN)
        
        if not links:
            await callback.message.edit_text(
                "🟡 روابط طلب الانضمام\n\n"
                "لا توجد روابط في هذه الفئة.",
                reply_markup=category_actions_keyboard(job_id, "request")
            )
            return
        
        links_text = "\n".join([
            f"{i+1}. {link.display_url or link.normalized_url[:50]}"
            for i, link in enumerate(links[:20])
        ])
        
        await callback.message.edit_text(
            f"🟡 روابط طلب الانضمام\n\n"
            f"عدد الروابط: {len(links)}\n\n"
            f"{links_text}",
            reply_markup=category_actions_keyboard(job_id, "request")
        )

@router.callback_query(lambda c: c.data.startswith("analysis:invalid:"))
async def show_invalid_links(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    async with get_db() as db:
        link_repo = WhatsAppLinkRepository(db)
        
        links = link_repo.get_by_status(LinkStatus.INVALID)
        
        await callback.message.edit_text(
            f"🔴 روابط غير صالحة\n\n"
            f"عدد الروابط: {len(links)}\n\n"
            f"تم استبعاد {len(links)} رابط.",
            reply_markup=invalid_links_keyboard(job_id)
        )

@router.callback_query(lambda c: c.data.startswith("analysis:other:"))
async def show_other_links(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    await callback.message.edit_text(
        "⚪ حالات أخرى\n\n"
        "هذه الروابط لم يتم تصنيفها ضمن\n"
        "الانضمام المباشر أو طلب الانضمام أو\n"
        "غير الصالحة.\n\n"
        "الأسباب المحتملة:\n"
        "• خطأ مؤقت\n"
        "• تعذر التحقق\n"
        "• حالة غير معروفة\n"
        "• تغيير في الرابط\n"
        "• قيود مؤقتة",
        reply_markup=other_links_keyboard(job_id)
    )

@router.callback_query(lambda c: c.data.startswith("analysis:back:"))
async def back_to_analysis_results(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    await callback.message.edit_text(
        "✅ اكتمل فحص الروابط\n\n"
        "يمكنك الآن استعراض النتائج.",
        reply_markup=analysis_results_keyboard(job_id)
    )

@router.callback_query(lambda c: c.data.startswith("analysis:rescan:"))
async def rescan_links(callback: CallbackQuery):
    await callback.answer()
    job_id = callback.data.split(":")[2]
    
    await callback.message.edit_text(
        "🔄 جاري إعادة فحص الروابط...",
        reply_markup=None
    )