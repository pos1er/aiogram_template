from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.utils.i18n import I18nMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update
from aiogram.dispatcher.flags import get_flag
from bot.mongodb import ForFilters
from cachetools import TTLCache

from bot.utils.loggers import app_logger



class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        app_logger.warning(data)
        app_logger.warning(event)
        user_language = await ForFilters().get_language()
        if not user_language:
            user_language = 'en'
        else:
            user_language = user_language['language']
        return user_language
