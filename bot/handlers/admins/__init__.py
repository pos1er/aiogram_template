from aiogram import Router

from bot.filters.private_chat import IsPrivate

from .any_admin import any_admin_router
from .no_access import no_access_router

admins_router = Router()

admins_router.include_router(any_admin_router)

admins_router.include_router(no_access_router)

admins_router.message.filter(IsPrivate())