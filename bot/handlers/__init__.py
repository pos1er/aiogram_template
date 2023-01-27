from aiogram import Router

from .users import users_router
from .admins import admins_router

router = Router()

router.include_router(users_router)
router.include_router(admins_router)
