import datetime
from dateutil.tz import gettz
from typing import Dict, Union

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import I18n
from aiogram import F, html, Router

from bot.data.config import DEFAULT_LANGUAGE
from bot.filters.admins import AdminFilter
from bot.filters.private_chat import IsPrivate
from bot.loader import bot
from bot.mongodb.admins import clear_waiting_chat, admins_list
from bot.mongodb.admin_keyboards import admin_main_menu, admin_settings_menu
from bot.mongodb.utils import get_id_database
from bot.states.admin import AdminSettings, AdminStates
from bot.utils.workdir import WORKDIR
from mongodb.gettings import get_language


any_admin_router = Router()
any_admin_router.message.filter(AdminFilter(''), IsPrivate())
any_admin_router.callback_query.filter(AdminFilter(''))


async def notification(notification_id: str, data: Dict, notification: str, user_id: Union[int, None] = None, additional_data: Union[Dict, None] = None):
    admin_list = await admins_list(notification=notification)
    i18n = I18n(path=WORKDIR / "locales",
                default_locale=DEFAULT_LANGUAGE, domain='messages')
    _ = i18n.gettext
    for admin in admin_list:
        language = await get_language(admin['user_id'])
        if notification_id == 'withdraw':
            text = _('''<b>💸 Вывод средств #{withdraw_num}</b>\n
<b>⚖️ Платежная система</b>: <code>{payment_system_text}</code>
<b>💳 Кошелек</b>: <code>{wallet}</code>
<b>💵 Валюта</b>: <code>{currency_text}</code>
<b>💰 Сумма</b>: <code>{amount}</code>\n
<b>🅰️ Администратор</b>: {admin}''', locale=language).format(**data)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("✅ ОТПРАВЛЕНО", locale=language), callback_data='_adminwithdraw')
                ]
            ])
        elif notification_id == 'purchase':
            text = _('''<b>💰 Новая покупка #{purchase_num}</b>\n
<b>👤 Пользователь</b>: {user}
<b>🛒 Товар</b>: <code>{name}</code>
<b>💰 Цена</b>: <code>{price}</code>
<b>📦 Кол-во</b>: <code>{count} шт.</code>
<b>💵 Итоговая сумма</b>: <code>{total_price}</code>\n''', locale=language).format(**data)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        elif notification_id == 'payment':
            promo_code = "" if not additional_data['promo_code'] else _("\n<b>🎁 Промокод</b>: {promo}", locale=language).format(promo=additional_data['promo_code'])
            ref_data = "" if not additional_data['referral'] else _("\n<b>👥 Реферал</b>: {ref}", locale=language).format(ref=additional_data['referral'])
            payid19 = ''
            if additional_data['ip'] and additional_data['email']:
                payid19 = _('\n\n<b>📧 Почта</b>: <code>{email}</code>\n<b>🥷 IP</b>: <code>{ip}</code>', 
                            locale=language).format(email=additional_data["email"], ip=additional_data["ip"])
            text = _('''<b>💳 Новое пополнение #{payment_id}</b>\n
<b>👤 Пользователь</b>: {user}
<b>💰 Сумма</b>: <code>{amount}{currency}</code> <b>({currency_code})</b>{ref_data}{promo_data}
<b>🪪 Платежная система</b>: <b>{payment_system}</b>{pay_id_data}''', locale=language).format(**data, promo_data=promo_code,
                                                                                              ref_data=ref_data, pay_id_data=payid19)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        elif notification_id == 'payment_cancel':
            promo_code = "" if not additional_data['promo_code'] else _("\n<b>🎁 Промокод</b>: {promo}", locale=language).format(promo=additional_data['promo_code'])
            ref_data = "" if not additional_data['referral'] else _("\n<b>👥 Реферал</b>: {ref}", locale=language).format(ref=additional_data['referral'])
            payid19 = ''
            if additional_data['ip'] and additional_data['email']:
                payid19 = _('\n\n<b>📧 Почта</b>: <code>{email}</code>\n<b>🥷 IP</b>: <code>{ip}</code>', 
                            locale=language).format(email=additional_data["email"], ip=additional_data["ip"])
            text = _('''<b>💳 Отмена пополнения #{payment_id}</b>\n
<b>👤 Пользователь</b>: {user}
<b>💰 Сумма</b>: <code>{amount}{currency}</code> <b>({currency_code})</b>{ref_data}{promo_data}
<b>🪪 Платежная система</b>: <b>{payment_system}</b>{pay_id_data}''', locale=language).format(**data, promo_data=promo_code,
                                                                                              ref_data=ref_data, pay_id_data=payid19)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        elif notification_id == 'user_balance_edit':
            reasons = {'feedback': _("🏆 Отзыв", locale=language), 'payment_trouble': _("🤖 Ошибка бота", locale=language),
                       'qiwi': _("💰 Qiwi/Банк. карта", locale=language), 'else': _("🧷 Прочее", locale=language)}
            if additional_data['amount'] > 0:
                action = _('Пополнение', locale=language)
            else:
                action = _('Снятие с', locale=language)
            text = _('''<b>💰 {action} баланса #{action_id}</b>\n
<b>👤 Пользователь</b>: {user}
<b>🅰️ Администратор</b>: {admin}
<b>💰 Сумма</b>: <code>{amount_n}{currency}</code> <b>({currency_code})</b>
\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n
<b>📍 Причина</b>: <code>{reason}</code>
<b>📉 Баланс ДО</b>: <code>{balance_before}{currency_user}</code> <b>({currency_code_user})</b>
<b>📈 Баланс ПОСЛЕ</b>: <code>{balance_after}{currency_user}</code> <b>({currency_code_user})</b>''', locale=language).format(**data, amount_n=Utils().normalize(additional_data['amount']), action=action, reason=reasons[additional_data['reason']])
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        elif notification_id == 'user_used_promo':
            promo_types = {'payment_bonus': _('💳 <b>Бонус к пополнению</b>: <code>{sale}%</code>', locale=language).format(sale=additional_data['sale']),
                           'item_sale': _('💸 <b>Скидка</b>: <code>{sale}%</code>', locale=language).format(sale=additional_data['sale']),
                           'amount_bonus': _('💰 <b>На баланс</b>: <code>{sale}{symbol}</code> <b>({currency})</b>', locale=language).format(sale=additional_data['sale'],
                                                                                                                           symbol=additional_data['symbol'],
                                                                                                                           currency=additional_data['currency'])}
            text = _('''<b>🎁 Использование промокода #{promo_id}</b>\n
<b>👤 Пользователь</b>: {user}
{promo_type}''', locale=language).format(**data, promo_type=promo_types[additional_data['promo_type']])
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        elif notification_id == 'ban_user':
            text = _('''<b>🔴 Бан пользователя</b>\n
<b>👤 Пользователь</b>: {user}
<b>🅰️ Администратор</b>: {admin}''', locale=language).format(**data)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        elif notification_id == 'unban_user':
            text = _('''<b>🟢 Разбан пользователя</b>\n
<b>👤 Пользователь</b>: {user}
<b>🅰️ Администратор</b>: {admin}''', locale=language).format(**data)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("👤 ПОЛЬЗОВАТЕЛЬ", locale=language), callback_data=f"get_user@{user_id}")
                ]
            ])
        await bot.send_message(admin['user_id'], text=text, reply_markup=keyboard)
        

@any_admin_router.message(Command("admin"))
async def admin_start_menu_function(message: Message, state: FSMContext):
    await state.clear()
    text_menu = _(
        "🔸 <b><u>Вход прошел успешно</u></b>\n\n<b>Добро пожаловать, {}</b>").format(html.link(html.quote(message.from_user.full_name),
                                                                                               f"tg://user?id={message.from_user.id}"))
    await state.set_state(AdminStates.admin)
    admin_menu = await admin_main_menu()
    await clear_waiting_chat()
    await message.answer(text=text_menu, reply_markup=admin_menu)


@any_admin_router.message(F.text == __("🅰️ Админка"))
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    text_menu = _(
        "🔸 <b><u>Вход прошел успешно</u></b>\n\n<b>Добро пожаловать, {}</b>").format(html.link(html.quote(message.from_user.full_name),
                                                                                               f"tg://user?id={message.from_user.id}"))
    await state.set_state(AdminStates.admin)
    admin_menu = await admin_main_menu()
    # await rework_price_purchase()
    # await print_all_balances()
    await get_id_database('users')
    await clear_waiting_chat()
    await message.answer(text=text_menu, reply_markup=admin_menu)


@any_admin_router.callback_query(F.data == 'admin_menu')
async def admin_menu_function(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    text_menu = _("🔸 <b><u>Вход прошел успешно</u></b>\n\n<b>Добро пожаловать, {}</b>").format(
        html.link(html.quote(callback_query.from_user.full_name),
                  f"tg://user?id={callback_query.from_user.id}"))
    await state.set_state(AdminStates.admin)
    admin_menu = await admin_main_menu()
    await bot.edit_message_text(text=text_menu, reply_markup=admin_menu, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@any_admin_router.callback_query(F.data == 'settings', StateFilter(AdminStates, AdminSettings))
async def settings_menu_function(callback_query: CallbackQuery, state: FSMContext):
    settings_menu = await admin_settings_menu()
    await state.set_state(AdminSettings.settings)
    await callback_query.answer()
    await bot.edit_message_text(text=_('<b>⚙️ Настройки</b>'), reply_markup=settings_menu, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
