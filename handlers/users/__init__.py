from aiogram import Router

from .captcha_answer import captcha_router
from .start_menu import start_router

users_router = Router()

users_router.include_router(captcha_router)
users_router.include_router(start_router)
