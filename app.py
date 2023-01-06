from utils.notify_admins import on_startup_notify
from loader import bot
# from handlers.users.timers import CheckTime
from utils.default_commands import set_default_commands
from handlers.users import start_menu, admin_panel
from middlewares.throttling import ThrottlingMiddleware, BanAcceptCheck, LanguageCheck
from aiohttp.web import run_app
from aiohttp.web_app import Application

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram import Router, F, types
import asyncio
import logging

logger = logging.getLogger(__name__)

WEBHOOK_URL = f"https://pos1er.com/AAAA"

main_router = Router()


@main_router.message(F.text)
async def echo(message: types.Message):
    # Regular request, add bot: Bot to handler kwargs
    # await bot.send_message(message.chat.id, message.text)

    # or reply INTO webhook
    return bot.send_message(chat_id=message.chat.id, text=message.text)


@main_router.startup()
async def on_startup(bot, webhook_url: str):
    await on_startup_notify(bot)
    await set_default_commands(bot)
    await bot.set_webhook(webhook_url)
    print(await bot.get_webhook_info())


@main_router.shutdown()
async def on_shutdown(bot):
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    logging.warning("Bye!")


def main():
    from handlers import dp
    dp["webhook_url"] = WEBHOOK_URL
    dp.include_router(main_router)
    dp.include_router(start_menu.router)
    dp.include_router(admin_panel.router)
    dp.update.outer_middleware(BanAcceptCheck())
    dp.update.outer_middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(LanguageCheck())
    
    app = Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path="/AAAA")
    setup_application(app, dp, bot=bot)
    run_app(app, host="127.0.0.1", port=7771)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
