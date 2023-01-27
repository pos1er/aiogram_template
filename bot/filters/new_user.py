from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from bot.mongodb import ForFilters


class NewUser(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return not await ForFilters().old_user()
