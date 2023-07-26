import asyncio

from typing import Callable, Dict, Any, Awaitable, List, Union
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, TelegramObject
from aiogram.dispatcher.flags import get_flag
from bot.mongodb.gettings import tm_status_and_ban
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    caches = {
        "start": TTLCache(maxsize=10_000, ttl=2),
        "default": TTLCache(maxsize=10_000, ttl=0.5),
        "delete_me": TTLCache(maxsize=10_000, ttl=0.3)
    }

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key", default="default")
        if throttling_key is not None and throttling_key in self.caches:
            try:
                if data['event_from_user'].id in self.caches[throttling_key]:
                    return
            except:
                print(data)
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
        if await tm_status_and_ban(user_id):
            return await handler(event, data)


class MediaGroupMiddleware(BaseMiddleware):
    ALBUM_DATA: Dict[str, List[Message]] = {}

    def __init__(self, delay: Union[int, float] = 0.6):
        self.delay = delay

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        try:
            self.ALBUM_DATA[event.media_group_id].append(event)
            return  # Don't propagate the event
        except KeyError:
            self.ALBUM_DATA[event.media_group_id] = [event]
            await asyncio.sleep(self.delay)
            data["album"] = self.ALBUM_DATA.pop(event.media_group_id)

        return await handler(event, data)
