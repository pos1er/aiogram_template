from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext

from bot.mongodb.user_keyboards import languages_accept


class AcceptLanguage(BaseFilter):
    async def __call__(self, callback_query: CallbackQuery, state: FSMContext):
        return await languages_accept(callback_query.data)
