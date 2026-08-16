from aiogram.fsm.state import State, StatesGroup

class WalletStates(StatesGroup):
    MAIN = State()
    DIRECT = State()
    REQUEST = State()
    MANAGE = State()