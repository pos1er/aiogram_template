from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext

from bot.mongodb.filters import old_user, captcha_passed
from bot.mongodb.gettings import captcha_status


class NewUser(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        return (not await old_user() or not await captcha_passed()) and await captcha_status()
