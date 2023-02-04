import asyncio

from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update
from aiogram.dispatcher.flags import get_flag
from bot.mongodb import ForFilters
from cachetools import TTLCache
import gettext


class ThrottlingMiddleware(BaseMiddleware):
    caches = {
        "start": TTLCache(maxsize=10_000, ttl=2),
        "default": TTLCache(maxsize=10_000, ttl=0.5)
    }

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key", default="default")
        print(data)
        print(throttling_key)
        #  Потом сделать, чтобы для старта работало
        if throttling_key is not None and throttling_key in self.caches:
            print(1)
            if data['event_from_user'].id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][data['event_from_user'].id] = None
        return await handler(event, data)


class BanAcceptCheck(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_id = data['event_from_user'].id
        if not await ForFilters().user_check(user_id):
            return await handler(event, data)


class LanguageCheck(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_language = await ForFilters().get_language()
        if not user_language:
            user_language = 'en'
        else:
            user_language = user_language['language']
        translate = gettext.translation(
            user_language, 'bot/locales', languages=[user_language])
        data['_'] = translate.gettext
        return await handler(event, data)
