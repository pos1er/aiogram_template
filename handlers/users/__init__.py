from aiogram import Router

from .captcha_answer import captcha_router
from .start_menu import start_router

router = Router()

router.include_router(captcha_router)
router.include_router(start_router)
