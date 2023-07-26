from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from dacite import from_dict
from bot.mongodb.gettings import booking_status, captcha_status, tm_status

from mongodb.mongodb import admins, user_id
from bot.data.admins import AdminRights


admin_rights = admins.find_one({'user_id': user_id}, {
                                        '_id': False, 'rights': True})['rights']
admins_right = from_dict(AdminRights, admin_rights)


async def admin_main_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=_("💻 ПРОФИЛЬ"), callback_data="admin_profile"),
        InlineKeyboardButton(text=_("🛒 ТОВАРЫ"), callback_data="products_list") if admins_right.products else None,
        InlineKeyboardButton(text=_("🅰️ АДМИНЫ"), callback_data="admins_list") if admins_right.admins_view else None,
        InlineKeyboardButton(text=_("👤 ЮЗЕРЫ"), callback_data="users_list") if admins_right.users_edit else None,
        InlineKeyboardButton(text=_("📊 АНАЛИТИКА"), callback_data="analytics_today@general") if admins_right.analytics else None,
        InlineKeyboardButton(text=_("🎁 УТИЛИТЫ"), callback_data="utilites") if admins_right.promo_codes or admins_right.auction or admins_right.contest else None,
        InlineKeyboardButton(text=_("✉️ РАССЫЛКА"), callback_data="mailing_menu") if admins_right.mailing else None,
        InlineKeyboardButton(text=_("🎞 ИСТОРИЯ"), callback_data="history") if admins_right.history or admins_right.replacement else None,
        InlineKeyboardButton(text=_("💸 БАЛАНС"), callback_data="balance") if admins_right.payment_system else None,
        InlineKeyboardButton(text=_("⚙️ НАСТРОЙКИ"), callback_data="settings")
        ]
    buttons = [x for x in buttons if x is not None]
    keyboard.add(*buttons)
    keyboard.adjust(1, 2)
    return keyboard.as_markup()


async def admin_settings_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    status_captcha = await captcha_status()
    status_captcha_text = '🟢' if status_captcha else '🔴'
    status_booking = await booking_status()
    status_booking_text = '🟢' if status_booking else '🔴'
    status_tm = await tm_status()
    status_tm_text = '🟢' if status_tm else '🔴'
    buttons = [
        InlineKeyboardButton(text=_("🔔 УВЕДОМЛЕНИЯ"),
                                callback_data="notifications"),
        InlineKeyboardButton(text=_("🇺🇳 ЯЗЫКИ"),
                                callback_data="languages"),
        InlineKeyboardButton(text=_("⭕️ КНОПКИ"),
                                callback_data="buttons"),
        InlineKeyboardButton(text=_("📑 ТЕКСТА"),
                                callback_data="texts"),
        InlineKeyboardButton(text=_("💵 ВАЛЮТЫ"),
                                callback_data="currencies"),
        InlineKeyboardButton(text=_("💳 ПЛАТЕЖКИ"),
                                callback_data="payment_systems"),
        InlineKeyboardButton(text=_("🖼 КАРТИНКИ"),
                                callback_data="pictures"),
        InlineKeyboardButton(text=_("💬 КАНАЛЫ И ЧАТЫ"),
                                callback_data="channels_and_chats"),
        InlineKeyboardButton(text=_("{status_captcha} КАПЧА").format(status_captcha=status_captcha_text),
                                callback_data="captcha_edit"),
        InlineKeyboardButton(text=_("{status_booking} БРОНИРОВАНИЕ").format(status_booking=status_booking_text),
                                callback_data="booking_edit"),
        InlineKeyboardButton(text=_("{status_tm} ТЕХ. РАБОТЫ").format(status_tm=status_tm_text),
                                callback_data="tm_edit"),
        InlineKeyboardButton(text=_("👈 НАЗАД"),
                                callback_data="admin_menu")
    ]
    if not admins_right.bot_config:
        del buttons[1:-1]
    if not admins_right.notifications:
        buttons.pop(0)
    keyboard.add(*buttons)
    keyboard.adjust(2)
    return keyboard.as_markup()