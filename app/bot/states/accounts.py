from aiogram.fsm.state import State, StatesGroup

class AccountsStates(StatesGroup):
    LIST = State()
    TELEGRAM_ADD = State()
    TELEGRAM_PHONE = State()
    TELEGRAM_CODE = State()
    TELEGRAM_PASSWORD = State()
    WHATSAPP_ADD = State()
    WHATSAPP_NAME = State()
    WHATSAPP_URL = State()