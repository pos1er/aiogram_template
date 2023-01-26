import logging
from aiohttp import web
from middlewares.throttling import ThrottlingMiddleware, BanAcceptCheck, LanguageCheck
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from data.config import BASE_URL
from handlers.users.start_menu import start_router
from handlers.users.admin_panel import admin_router

logger = logging.getLogger(__name__)

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 7771
MAIN_BOT_PATH = "/test_bot"
REDIS_DSN = "redis://localhost:6379/0"


async def on_startup(dp, bot):
    logger.info('Bot startup')
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")
    
    await bot.send_message(1502268714, "<b>✅ Бот запущен</b>")


async def on_shutdown(dp, bot):
    logger.warning('Shutting down..')
    
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    
    await bot.send_message(1502268714, "<b>✅ Бот остановлен</b>")
    logger.warning('Bye!')


def main():
    from loader import bot, dp
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    dp.update.outer_middleware(BanAcceptCheck())
    dp.update.outer_middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(LanguageCheck())

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp,
                         bot=bot).register(app, path=MAIN_BOT_PATH)

    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
