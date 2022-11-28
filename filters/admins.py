from aiogram.filters import BaseFilter
from aiogram.types import Message
from mongodb import ForFilters
import time


class AdminFilter(BaseFilter):
    admin_type: str

    async def __call__(self, message: Message):
        if not self.admin_type:
            self.admin_type = ''

    async def check(self, message: Message) -> bool:
        return await self.check_admin(message, self.admin_type)

    @staticmethod
    async def check_admin(message: Message, admin_type) -> bool:
        return await ForFilters().admin_check(admin_type)
