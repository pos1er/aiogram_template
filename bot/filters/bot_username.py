from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext

from bot.mongodb.filters import check_bot_username



class UsernameFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return await check_bot_username(message.text)
