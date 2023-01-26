import logging
from typing import Any, Dict

import datetime
from captcha.services.captcha import CaptchaService
from captcha.services.captcha_generator import CaptchaGenerator
from captcha.services.captcha_scheduler import CaptchaScheduler
from captcha.services.lock_user import LockUserService
from data.config import REDIS_URL, CAPTCHA_DURATION


async def configure_services() -> Dict[str, Any]:
    lock_service=LockUserService(connection_uri = REDIS_URL)
    captcha_scheduler = CaptchaScheduler()
    captcha_generator = CaptchaGenerator()
    captcha = CaptchaService(
        lock_service,
        captcha_scheduler,
        captcha_generator,
        captcha_duration = datetime.timedelta(seconds=CAPTCHA_DURATION),
    )
    await captcha_scheduler.init(connection_uri=REDIS_URL)
    captcha_generator.load_emoji()
    return {"captcha": captcha}


def configure_logging() -> None:
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
