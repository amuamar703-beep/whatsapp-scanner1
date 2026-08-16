from aiogram.fsm.state import State, StatesGroup

class ExplorationStates(StatesGroup):
    WAITING_SOURCE = State()
    RESOLVING = State()
    READY = State()
    RUNNING = State()
    COMPLETED = State()