from datetime import datetime, timedelta
from aiohttp import web
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.i18n import I18n

from captcha.misc.configure import configure_logging, configure_services

from bot.utils.workdir import WORKDIR
from bot.data.config import BASE_URL
from bot.middlewares.throttling import ThrottlingMiddleware, BanAcceptCheck
from bot.middlewares.i18n import MyI18nMiddleware
from bot.loader import bot, dp, scheduler
from bot.handlers import router
from bot.handlers.admins import apscheduler
from bot.utils.loggers import app_logger

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 7771
MAIN_BOT_PATH = "/test_bot"


async def on_startup():
    app_logger.info('Bot startup')

    services = await configure_services()
    dp.workflow_data.update(services)
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")

    '''
    scheduler.add_job(apscheduler.send_message_interval,
                      trigger='interval', seconds=10)
                      
    scheduler.add_job(apscheduler.send_message_time, trigger='date',
                      run_date=datetime.now() + timedelta(seconds=10))
    '''
    scheduler.add_job(apscheduler.daily_message, trigger='cron',
                      hour=datetime.now().hour, minute=datetime.now().minute + 1, start_date=datetime.now())
    scheduler.start()
    await bot.send_message(1502268714, "<b>✅ Бот запущен</b>")

async def on_shutdown():
    app_logger.warning('Shutting down..')

    await bot.delete_webhook()
    await dp.storage.close()

    await bot.send_message(1502268714, "<b>✅ Бот остановлен</b>")
    app_logger.warning('Bye!')


def main():
    configure_logging()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(BanAcceptCheck())
    router.message.middleware(ChatActionMiddleware())
    
    i18n = I18n(path=WORKDIR / "locales", default_locale='ru', domain='messages')
    dp.update.outer_middleware(MyI18nMiddleware(i18n=i18n))
    
    dp.include_router(router)


    app = web.Application()
    SimpleRequestHandler(dispatcher=dp,
                         bot=bot).register(app, path=MAIN_BOT_PATH)

    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
