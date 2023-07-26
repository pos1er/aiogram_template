from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from bot.mongodb.mongodb import db_data


async def get_languages_menu(no_exit=False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    languages = db_data.find_one(
        {'id': 1}, {'_id': False, 'languages': True})['languages']
    for button in languages:
        keyboard.button(text=button["text"], callback_data=button["code"])
    if not no_exit:
        keyboard.row(InlineKeyboardButton(
            text=_('👈 Назад'), callback_data='settings'), width=1)
    keyboard.adjust(2)
    return keyboard.as_markup()


async def languages_accept() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    languages = db_data.find_one({'id': 1}, {'_id': False, 'languages': True})['languages']
    for button in languages:
        if button['status'] == True:
            keyboard.button(text=button["text"], callback_data=button["code"])
    keyboard.adjust(2)
    return keyboard.as_markup()