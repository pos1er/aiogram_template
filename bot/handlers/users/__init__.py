from aiogram import Router
from bot.filters.captcha_passed import CaptchaPassed

from bot.filters.language_choosen import LanguageChoosen
from bot.filters.private_chat import IsPrivate

from .captcha_answer import captcha_router
from .language_start import lang_router

language_router = Router()
users_router = Router()

language_router.include_router(captcha_router)
language_router.include_router(lang_router)

language_router.message.filter(IsPrivate())
users_router.message.filter(LanguageChoosen(), IsPrivate(), CaptchaPassed())
users_router.callback_query.filter(LanguageChoosen(), CaptchaPassed())
