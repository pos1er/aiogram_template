from loader import bot
# from handlers.users.timers import CheckTime
from utils.default_commands import set_default_commands
from handlers.users import start_menu, admin_panel
from middlewares.throttling import ThrottlingMiddleware, BanAcceptCheck, LanguageCheck
import asyncio
import logging

logger = logging.getLogger(__name__)


async def main():
    from handlers import dp
    try:
        # dp.loop.create_task(CheckTime(10).start_all())
        from utils.notify_admins import on_startup_notify
        await on_startup_notify(bot)
        await set_default_commands(bot)
        dp.include_router(start_menu.router)
        dp.include_router(admin_panel.router)
        dp.update.outer_middleware(BanAcceptCheck())
        dp.update.outer_middleware(ThrottlingMiddleware())
        dp.update.outer_middleware(LanguageCheck())

        await dp.start_polling(bot, dispatcher=dp, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        # await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
