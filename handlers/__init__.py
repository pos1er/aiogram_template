from aiogram import Router

from .users import router as users_router
from .admins import router as admins_router

router = Router()

router.include_router(users_router)
router.include_router(admins_router)
