from typing import Dict, List
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import get_i18n
from aiogram.filters.command import Command
from aiogram import F
from bot.filters.captcha_passed import CaptchaPassed
from bot.filters.language_choosen import LanguageChoosen
from bot.filters.private_chat import IsPrivate

from bot.loader import bot
from bot.keyboards.inline.user import delete_me
from bot.mongodb.gettings import get_faq
from bot.mongodb.user_keyboards import get_languages_menu
from bot.states.user import ProfileStates

else_buttons_router = Router()
else_buttons_router.message.filter(IsPrivate(), CaptchaPassed(), LanguageChoosen())
else_buttons_router.callback_query.filter(CaptchaPassed(), LanguageChoosen())


@else_buttons_router.message(Command("language"))
async def languages_function(message: Message, state: FSMContext):
    await state.clear()
    languages_menu = await get_languages_menu(no_exit=True)
    await state.set_state(ProfileStates.languages)
    await bot.send_message(text=_('<b>🇺🇳 Языки</b>'), reply_markup=languages_menu, chat_id=message.from_user.id)


@else_buttons_router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    await state.clear()
    language = get_i18n().current_locale
    faq = await get_faq()
    help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_('📞 Написать саппорту'), url="https://t.me/qshopsupport")
        ]])
    await message.answer(text=faq[language], reply_markup=help_keyboard, disable_web_page_preview=True)


@else_buttons_router.message(F.text == __("⚡️ Наши каналы"))
async def our_channels(message: Message, state: FSMContext):
    await state.clear()
    rules = _('''⚡️ <b>Официальный канал:</b> @QShopQ\n\n👥 <b>Тема на LOLZTEAM:</b> https://zelenka.guru/threads/4658475/''')
    await message.answer(text=rules, disable_web_page_preview=True)


@else_buttons_router.message(F.text == __("❓ Помощь"))
async def help_menu(message: Message, state: FSMContext):
    await state.clear()
    language = get_i18n().current_locale
    faq = await get_faq()
    help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_('📞 Написать саппорту'), url="https://t.me/qshopsupport")
        ]])
    await message.answer(text=faq[language], reply_markup=help_keyboard, disable_web_page_preview=True)


@else_buttons_router.message(F.text == __("💰 1$ на баланс"))
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    text = _('''<b>💰 Для того, чтобы получить 1$ на баланс:</b>\n
1. Соверши любую покупку стоимостью более <code>1$</code>
2. Оставь отзыв на <b>LOLZTEAM</b> (ОБЯЗАТЕЛЬНО! Прикрепить скриншот оплаты, чек покупки и сам аккаунт) 👇
https://zelenka.guru/threads/4658475/
3. Отправь <b>чек</b> и <b>скриншот отзыва</b> саппорту — @QShopSupport''')
    await message.answer(text=text, reply_markup=delete_me(), disable_web_page_preview=True)


@else_buttons_router.callback_query(F.data == "delete_me", flags={"throttling_key": "delete_me"})
async def delete_me_func(callback_query: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
