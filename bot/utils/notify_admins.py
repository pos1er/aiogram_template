import logging

from aiogram import Bot


async def on_startup_notify(bot: Bot):
    try:
        await bot.send_message(1502268714, "<b>✅ Бот запущен</b>")

    except Exception as err:
        logging.exception(err)