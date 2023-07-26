from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    admin = State()
    settings = State()

class AdminSettings(StatesGroup):
    settings = State()