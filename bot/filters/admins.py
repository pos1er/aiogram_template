from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.mongodb import ForFilters


class AdminFilter(BaseFilter):
    admin_right: str = ''

    async def __call__(self, message: Message):
        return await self.check(message)

    async def check(self, message: Message) -> bool:
        return await self.check_admin(message, self.admin_right)

    @staticmethod
    async def check_admin(message: Message, admin_right) -> bool:
        return await ForFilters().admin_check(admin_right)
