from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    language_choice = State()
