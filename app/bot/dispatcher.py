from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.core.config import settings
from app.bot.handlers import start, explorer, scanner, wallet, accounts, settings as settings_handler, jobs, export, whatsapp_send, admin

bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

dp.register_message_handler(start.cmd_start, commands=["start"])
dp.register_message_handler(start.cmd_help, commands=["help"])
dp.register_message_handler(start.cmd_explore, commands=["explore"])
dp.register_message_handler(start.cmd_wallet, commands=["wallet"])
dp.register_message_handler(start.cmd_jobs, commands=["jobs"])
dp.register_message_handler(start.cmd_settings, commands=["settings"])
dp.register_message_handler(start.cmd_admin, commands=["admin"])

dp.register_callback_query_handler(explorer.start_exploration_callback, lambda c: c.data == "explore:start")
dp.register_callback_query_handler(explorer.run_exploration, lambda c: c.data.startswith("explore:run:"))
dp.register_callback_query_handler(explorer.change_source, lambda c: c.data == "explore:change")
dp.register_callback_query_handler(explorer.cancel_exploration, lambda c: c.data == "explore:cancel")
dp.register_callback_query_handler(explorer.retry_exploration, lambda c: c.data == "explore:retry")
dp.register_callback_query_handler(explorer.show_results, lambda c: c.data.startswith("explore:results:"))

dp.register_callback_query_handler(scanner.start_analysis, lambda c: c.data.startswith("analysis:start:"))
dp.register_callback_query_handler(scanner.confirm_analysis, lambda c: c.data.startswith("analysis:confirm:"))
dp.register_callback_query_handler(scanner.show_direct_links, lambda c: c.data.startswith("analysis:direct:"))
dp.register_callback_query_handler(scanner.show_request_links, lambda c: c.data.startswith("analysis:request:"))
dp.register_callback_query_handler(scanner.show_invalid_links, lambda c: c.data.startswith("analysis:invalid:"))
dp.register_callback_query_handler(scanner.show_other_links, lambda c: c.data.startswith("analysis:other:"))

dp.register_callback_query_handler(wallet.open_wallet, lambda c: c.data == "wallet:open")
dp.register_callback_query_handler(wallet.wallet_direct_links, lambda c: c.data == "wallet:direct")
dp.register_callback_query_handler(wallet.wallet_request_links, lambda c: c.data == "wallet:request")
dp.register_callback_query_handler(wallet.wallet_stats, lambda c: c.data == "wallet:stats")
dp.register_callback_query_handler(wallet.wallet_back, lambda c: c.data == "wallet:back")
dp.register_callback_query_handler(wallet.wallet_delete_confirm, lambda c: c.data.startswith("wallet:delete:"))

dp.register_callback_query_handler(settings_handler.open_settings, lambda c: c.data == "settings:open")
dp.register_callback_query_handler(settings_handler.settings_back, lambda c: c.data == "settings:back")

dp.register_callback_query_handler(jobs.view_jobs, lambda c: c.data == "jobs:open")
dp.register_callback_query_handler(jobs.jobs_back, lambda c: c.data == "jobs:back")

dp.register_callback_query_handler(accounts.open_accounts, lambda c: c.data == "accounts:open")

dp.register_callback_query_handler(export.export_select_format, lambda c: c.data.startswith("export:start:"))

dp.register_callback_query_handler(whatsapp_send.wallet_send_whatsapp, lambda c: c.data.startswith("wallet:send:"))

dp.register_callback_query_handler(admin.admin_panel, lambda c: c.data == "admin:open")

async def set_commands():
    commands = [
        BotCommand(command="start", description="بدء البوت والقائمة الرئيسية"),
        BotCommand(command="help", description="المساعدة"),
        BotCommand(command="explore", description="استكشاف روابط WhatsApp"),
        BotCommand(command="wallet", description="عرض المحفظة"),
        BotCommand(command="jobs", description="عرض المهام الحالية"),
        BotCommand(command="settings", description="الإعدادات"),
        BotCommand(command="admin", description="لوحة الإدارة"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    await set_commands()

async def on_shutdown():
    await bot.close()
