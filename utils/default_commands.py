from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Главное меню")
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
