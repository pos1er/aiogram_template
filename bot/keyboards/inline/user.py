from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

language_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
        InlineKeyboardButton(text="🇺🇦 Українська", callback_data="ua")
        
    ],
    [
        InlineKeyboardButton(text="🇬🇧 English", callback_data="en"),
        InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="de")
    ],
])


def delete_me():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("❌ Закрыть"), callback_data="delete_me")
        ]
    ])


def profile_keyboard(_, user_language=None):
    if not user_language:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=_("💻 Профиль"), callback_data="profile_all")
            ]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=_("💻 Профиль", locale=user_language), callback_data="profile_all")
            ]
        ])