from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter

from bot.mongodb.filters import ranks_check


class RanksFilter(BaseFilter):
    async def __call__(self, query: CallbackQuery):
        return await ranks_check(query.data)