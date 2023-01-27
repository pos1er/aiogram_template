from typing import Any, Dict, cast

from bot.loader import bot
from data.config import REDIS_URL
from arq import run_worker
from arq.connections import RedisSettings
from arq.typing import WorkerSettingsType

from captcha.services.lock_user import LockUserService
from captcha.tasks.join_expired import join_expired_task


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


if __name__ == "__main__":
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    settings_cls = cast(WorkerSettingsType, WorkerSettings)
    run_worker(settings_cls, redis_settings=redis_settings)
