from aiohttp import web
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from captcha.misc.configure import configure_logging, configure_services

from bot.data.config import BASE_URL
from bot.middlewares.throttling import ThrottlingMiddleware, BanAcceptCheck, LanguageCheck
from bot.loader import bot, dp
from bot.handlers import router
from bot.utils.loggers import app_logger

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 7771
MAIN_BOT_PATH = "/test_bot"
#DOCKER

async def on_startup():
    app_logger.info('Bot startup')

    services = await configure_services()
    dp.workflow_data.update(services)
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")

    await bot.send_message(1502268714, "<b>✅ Бот запущен</b>")

async def on_shutdown():
    app_logger.warning('Shutting down..')

    await bot.delete_webhook()
    await dp.storage.close()

    await bot.send_message(1502268714, "<b>✅ Бот остановлен</b>")
    app_logger.warning('Bye!')


def main():
    configure_logging()
    dp.include_router(router)

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
    main()
