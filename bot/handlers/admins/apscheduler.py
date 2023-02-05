from aiogram import Bot
from bot.mongodb import MainGets
from bot.utils.loggers import app_logger


async def send_message_time(bot: Bot):
    admins_list = await MainGets().get_admins_list('notifications.after_start_bot')
    app_logger.warning(admins_list)
    for admin in admins_list:
        await bot.send_message(admin['id'], text='Это сообщение отправлено через несколько секунд после старта бота')

'''
After start bot message



Interval bot message


'''


async def send_message_interval(bot: Bot):
    admins_list = await MainGets().get_admins_list('notifications.interval_bot')
    app_logger.warning(admins_list)
    for admin in admins_list:
        await bot.send_message(admin['id'], text='Это сообщение будет отпавляться с интервалом в 1 минуту')

async def daily_message(bot: Bot):
    admins_list = await MainGets().get_admins_list('notifications.daily')
    app_logger.warning(admins_list)
    for admin in admins_list:
        await bot.send_message(admin['id'], text='Это сообщение будет отправляться ежедневно в указанное время')
