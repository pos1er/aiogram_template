from dataclasses import dataclass
from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.mongodb.filters import admin_check, admin_waiting

@dataclass
class AdminFilter(BaseFilter):
    admin_right: str
    
    async def __call__(self, message: Message):
        return await admin_check(self.admin_right)

@dataclass
class AdminWaitingChat(BaseFilter):
    async def __call__(self, message: Message):
        return await admin_waiting(message.from_user.id)