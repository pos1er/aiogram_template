from typing import Any, Dict, cast
from aiohttp import web
from middlewares.throttling import ThrottlingMiddleware, BanAcceptCheck, LanguageCheck
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
import asyncio

from captcha.misc.configure import configure_logging, configure_services

from loader import bot, dp
from data.config import BASE_URL, REDIS_URL
from handlers import router
from utils.loggers import app_logger

from arq import run_worker
from arq.connections import RedisSettings
from arq.typing import WorkerSettingsType

from captcha.services.lock_user import LockUserService
from captcha.worker.tasks.join_expired import join_expired_task

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 7771
MAIN_BOT_PATH = "/test_bot"
REDIS_DSN = "redis://localhost:6379/0"


async def startup(ctx: Dict[str, Any]):
    ctx["bot"] = bot
    ctx["lock_user_service"] = LockUserService(
        connection_uri=REDIS_URL,
    )


async def shutdown(ctx: Dict[str, Any]):
    bot = ctx.pop("bot")
    await bot.session.close()


class WorkerSettings:
    on_startup = startup
    on_shutdown = shutdown
    functions = [join_expired_task]
    allow_abort_jobs = True


async def on_startup():
    app_logger.info('Bot startup')

    services = await configure_services()
    dp.workflow_data.update(services)
    await bot.set_webhook(f"{BASE_URL}{MAIN_BOT_PATH}")

    await bot.send_message(1502268714, "<b>✅ Бот запущен</b>")


async def on_startup_both():
    tasks = [asyncio.ensure_future(on_startup_redis()), asyncio.ensure_future(on_startup())]
    await asyncio.gather(*tasks)

async def on_startup_redis():
    app_logger.info('Redis started..')
    
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    settings_cls = cast(WorkerSettingsType, WorkerSettings)
    run_worker(settings_cls, redis_settings=redis_settings)

async def on_shutdown():
    app_logger.warning('Shutting down..')

    await bot.delete_webhook()
    await dp.storage.close()

    await bot.send_message(1502268714, "<b>✅ Бот остановлен</b>")
    app_logger.warning('Bye!')


def main():
    configure_logging()
    dp.include_router(router)

    dp.startup.register(on_startup_both)
    dp.shutdown.register(on_shutdown)

    dp.update.outer_middleware(BanAcceptCheck())
    dp.update.outer_middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(LanguageCheck())

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp,
                         bot=bot).register(app, path=MAIN_BOT_PATH)

    setup_application(app, dp, bot=bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(on_startup_redis())
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
