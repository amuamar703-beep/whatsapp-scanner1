from aiogram.fsm.state import State, StatesGroup

class SettingsStates(StatesGroup):
    MAIN = State()
    EXPLORATION = State()
    NOTIFICATIONS = State()
    DATA = State()