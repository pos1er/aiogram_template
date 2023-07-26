from aiogram import Router

from .users.start_menu import start_router
from .users.else_buttons import else_buttons_router
from .users import users_router, language_router
from .admins import admins_router
from .admins.any_admin import any_admin_router

router = Router()

router.include_router(any_admin_router)
router.include_router(language_router)
router.include_router(start_router)
router.include_router(else_buttons_router)
router.include_router(users_router)
router.include_router(admins_router)
