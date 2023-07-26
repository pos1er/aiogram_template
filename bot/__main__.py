from datetime import datetime, timedelta
from aiohttp import web
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.i18n import I18n
from aiogram import html

from captcha.misc.configure import configure_logging, configure_services

from bot.utils.workdir import WORKDIR
from bot.data.config import BASE_URL, WEB_SERVER_PORT, BOT_PATH, TESTING_BOT, MAIN_ADMIN_ID, DEFAULT_LANGUAGE
from bot.middlewares.throttling import MediaGroupMiddleware, ThrottlingMiddleware, BanAcceptCheck
from bot.middlewares.i18n import MyI18nMiddleware
from bot.loader import bot, dp
from bot.handlers import router
from bot.handlers.admins import apscheduler
from bot.utils.loggers import app_logger
from bot.utils.default_commands import set_default_commands

WEB_SERVER_HOST = "127.0.0.1"
MAIN_BOT_PATH = f"/{BOT_PATH}"


async def on_startup():
    app_logger.info('Bot startup')

    await set_default_commands(bot)
    services = await configure_services()
    dp.workflow_data.update(services)
    if not TESTING_BOT:
        await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")
        
        from bot.loader import scheduler
        '''
        scheduler.add_job(apscheduler.send_message_interval,
                        trigger='interval', seconds=10)
                        
        scheduler.add_job(apscheduler.send_message_time, trigger='date',
                        run_date=datetime.now() + timedelta(seconds=10))
        '''
        scheduler.start()
        
        if not scheduler.get_job('daily'):
            scheduler.add_job(apscheduler.daily_message, trigger='cron', hour=0, minute=0, id='daily')

        # app_logger.warning(scheduler.get_jobs())
    
    await bot.send_message(MAIN_ADMIN_ID, html.bold("✅ Бот запущен"))

async def on_shutdown():
    app_logger.warning('Shutting down..')

    if not TESTING_BOT:
        from bot.loader import scheduler
        await bot.delete_webhook()
        scheduler.shutdown(wait=False)
    
    await dp.storage.close()
    
    await bot.send_message(MAIN_ADMIN_ID, html.bold("✅ Бот остановлен"))
    app_logger.warning('Bye!')


def main():
    configure_logging()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(MediaGroupMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    dp.message.outer_middleware(BanAcceptCheck())
    dp.callback_query.outer_middleware(BanAcceptCheck())
    
    router.message.middleware(ChatActionMiddleware())
    
    default_locale = DEFAULT_LANGUAGE
    i18n = I18n(path=WORKDIR / "locales", default_locale=default_locale, domain='messages')
    
    dp.message.outer_middleware(MyI18nMiddleware(i18n=i18n))
    dp.callback_query.outer_middleware(MyI18nMiddleware(i18n=i18n))
    
    dp.include_router(router)

    if TESTING_BOT:
        dp.run_polling(bot)
    else:
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp,
                            bot=bot).register(app, path=MAIN_BOT_PATH)

        setup_application(app, dp, bot=bot)
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
