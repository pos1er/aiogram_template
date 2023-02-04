from aiogram import Bot, Dispatcher, flags, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, Update
from cachetools import TTLCache

TOKEN = "5539915247:AAFPAi6M3_mtRGxzTjebJGm3DQU72Q2Ga2c"
dp = Dispatcher()


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
        print(throttling_key)
        if throttling_key is not None and throttling_key in self.caches:
            if data['event_from_user'].id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][data['event_from_user'].id] = None
        return await handler(event, data)



async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


def main() -> None:
    bot = Bot(TOKEN, parse_mode="HTML")
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.register(command_start_handler, CommandStart(),
                        flags={"throttling_key": "start"})
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
