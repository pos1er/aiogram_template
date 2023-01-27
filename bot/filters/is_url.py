from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsUrl(BaseFilter):
    async def __call__(self, message: Message, *args):
        return [True for elem in message.entities if elem.type == 'url']
