from aiogram.fsm.state import State, StatesGroup

class AnalysisStates(StatesGroup):
    CONFIRM = State()
    RUNNING = State()
    COMPLETED = State()
    VIEWING = State()