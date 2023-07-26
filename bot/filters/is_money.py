from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsMoney(BaseFilter):
    async def __call__(self, message: Message, *args):
        try:
            if message.text:
                amount = float(message.text)
                if amount <= 0:
                    return False
                else:
                    return True
        except ValueError:
            return None


