from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import get_i18n
from bot.mongodb.mongodb import db_data

def start_menu_keyboard(locale=False):
    if not locale:
        locale = get_i18n().current_locale
    buttons_data = db_data.find_one({'id': 1}, {'_id': False, 'buttons': True})['buttons']
    if buttons_data['review'] and buttons_data['team']:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=_("🛒 Купить", locale=locale)),
                    KeyboardButton(text=_("📜 Наличие товаров", locale=locale))
                ],
                [
                    KeyboardButton(text=_("💻 Профиль", locale=locale)),
                    KeyboardButton(text=_("💠 Проблема с товаром", locale=locale))
                ],
                [
                    KeyboardButton(text=_("❓ Помощь", locale=locale)),
                    KeyboardButton(text=_("💰 1$ на баланс", locale=locale))
                ],
                [
                    KeyboardButton(text=_("⚡️ Наши каналы", locale=locale)),
                    KeyboardButton(text=_("🎗 QTeam - PayPal", locale=locale))
                ]
            ],
            resize_keyboard=True
        )
    elif buttons_data['review']:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=_("🛒 Купить", locale=locale)),
                    KeyboardButton(text=_("📜 Наличие товаров", locale=locale))
                ],
                [
                    KeyboardButton(text=_("💻 Профиль", locale=locale)),
                    KeyboardButton(text=_("💠 Проблема с товаром", locale=locale))
                ],
                [
                    KeyboardButton(text=_("❓ Помощь", locale=locale)),
                    KeyboardButton(text=_("💰 1$ на баланс", locale=locale))
                ],
                [
                    KeyboardButton(text=_("⚡️ Наши каналы", locale=locale))
                ]
            ],
            resize_keyboard=True
        )
    elif buttons_data['team']:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=_("🛒 Купить", locale=locale)),
                    KeyboardButton(text=_("📜 Наличие товаров", locale=locale))
                ],
                [
                    KeyboardButton(text=_("💻 Профиль", locale=locale)),
                    KeyboardButton(text=_("💠 Проблема с товаром", locale=locale))
                ],
                [
                    KeyboardButton(text=_("❓ Помощь", locale=locale)),
                    KeyboardButton(text=_("🎗 QTeam - PayPal", locale=locale))
                ],
                [
                    KeyboardButton(text=_("⚡️ Наши каналы", locale=locale))
                ]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=_("🛒 Купить", locale=locale)),
                    KeyboardButton(text=_("📜 Наличие товаров", locale=locale))
                ],
                [
                    KeyboardButton(text=_("💻 Профиль", locale=locale)),
                    KeyboardButton(text=_("💠 Проблема с товаром", locale=locale))
                ],
                [
                    KeyboardButton(text=_("❓ Помощь", locale=locale)),
                    KeyboardButton(text=_("⚡️ Наши каналы", locale=locale))
                ]
            ],
            resize_keyboard=True
        )
