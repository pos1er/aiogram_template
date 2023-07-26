from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import get_i18n

def start_admin_menu_keyboard(locale=False):
    if not locale:
        locale = get_i18n().current_locale
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
            ],
            [
                KeyboardButton(text=_("🅰️ Админка", locale=locale))
            ]
        ],
        resize_keyboard=True
    )
