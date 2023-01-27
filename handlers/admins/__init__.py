from aiogram import Router

from .any_admin import any_admin_router

router = Router()

router.include_router(any_admin_router)
