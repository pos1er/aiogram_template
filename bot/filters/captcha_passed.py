from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext

from bot.mongodb.filters import captcha_passed


class CaptchaPassed(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return await captcha_passed()
