from aiogram.fsm.state import State, StatesGroup

class ExportStates(StatesGroup):
    SELECT_FORMAT = State()
    GENERATING = State()