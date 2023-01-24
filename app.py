from os import getenv
from typing import Any, Dict, Union

from aiohttp import web
from handlers.users.start_menu import start_router

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters import Command, CommandObject
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import Message
from aiogram.utils.token import TokenValidationError, validate_token
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)
from data.config import TOKEN

main_router = Router()

BASE_URL = getenv("BASE_URL", "https://pos1er.com")

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 7771
MAIN_BOT_PATH = "/AAAA"
# OTHER_BOTS_PATH = "/webhook/bot/{bot_token}"
REDIS_DSN = "redis://localhost:6379/0"

# OTHER_BOTS_URL = f"{BASE_URL}{OTHER_BOTS_PATH}"


def is_bot_token(value: str) -> Union[bool, Dict[str, Any]]:
    try:
        validate_token(value)
    except TokenValidationError:
        return False
    return True


@main_router.message(Command(commands=["add"], magic=F.args.func(is_bot_token)))
async def command_add_bot(message: Message, command: CommandObject, bot: Bot) -> Any:
    new_bot = Bot(token=command.args, session=bot.session)
    try:
        bot_user = await new_bot.get_me()
    except TelegramUnauthorizedError:
        return message.answer("Invalid token")
    await new_bot.delete_webhook(drop_pending_updates=True)
    # await new_bot.set_webhook(OTHER_BOTS_URL.format(bot_token=command.args))
    return await message.answer(f"Bot @{bot_user.username} successful added")


@main_router.message(Command(commands=["start"]))
async def start_command(message: Message, command: CommandObject, bot: Bot) -> Any:
    return await message.answer(f"Bot")


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")


def main():
    session = AiohttpSession()
    bot_settings = {"session": session, "parse_mode": "HTML"}
    bot = Bot(token=TOKEN, **bot_settings)
    storage = RedisStorage.from_url(
        REDIS_DSN, key_builder=DefaultKeyBuilder(with_bot_id=True))

    main_dispatcher = Dispatcher(storage=storage)
    main_dispatcher.include_router(main_router)
    main_dispatcher.startup.register(on_startup)

    multibot_dispatcher = Dispatcher(storage=storage)
    multibot_dispatcher.include_router(start_router)

    app = web.Application()
    SimpleRequestHandler(dispatcher=main_dispatcher,
                         bot=bot).register(app, path=MAIN_BOT_PATH)
    # TokenBasedRequestHandler(
    #     dispatcher=multibot_dispatcher,
    #     bot_settings=bot_settings,
    # ).register(app, path=OTHER_BOTS_PATH)

    setup_application(app, main_dispatcher, bot=bot)
    setup_application(app, multibot_dispatcher)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
