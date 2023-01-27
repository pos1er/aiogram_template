from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext


class IsPrivate(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return message.chat.type == 'private'
