from aiogram.types import Message
from aiogram.enums.chat_type import ChatType
from aiogram.filters import BaseFilter


class IsGroup(BaseFilter):
    async def __call__(self, message: Message, *args):
        return message.chat.type in [
            ChatType.GROUP,
            ChatType.SUPERGROUP
        ]
