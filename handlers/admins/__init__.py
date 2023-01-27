from aiogram import Router

from .any_admin import any_admin_router

admins_router = Router()

admins_router.include_router(any_admin_router)
