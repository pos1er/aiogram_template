from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import F, html, Router

from filters.private_chat import IsPrivate
from filters.admins import AdminFilter

from keyboards.inline.admin import admin_menu
from keyboards.inline.user import delete_me
from loader import dp, bot
from mongodb import Admins, MainGets
from states.admin import AdminStates


any_admin_router = Router()
any_admin_router.message.filter(IsPrivate(), AdminFilter())


@any_admin_router.message(Command("admin"))
async def admin_menu_function(message: Message, state: FSMContext):
    await state.clear()
    text_menu = f'''<u>Вход прошел успешно</u>\n
<b>Добро пожаловать, {message.from_user.full_name}</b>'''
    await state.set_state(AdminStates.admin)
    await message.answer(text=text_menu, reply_markup=admin_menu)


@any_admin_router.callback_query(F.data == 'admin')
async def admin_menu_function(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    text_menu = f'''<u>Вход прошел успешно</u>\n
<b>Добро пожаловать, {callback_query.from_user.full_name}</b>'''
    await state.set_state(AdminStates.admin)
    await bot.send_message(text=text_menu, reply_markup=admin_menu, chat_id=callback_query.from_user.id)


@any_admin_router.callback_query(F.data == 'settings')
async def settings_menu_function(callback_query: CallbackQuery, state: FSMContext):
    captcha_status = await MainGets().captcha_status()
    if captcha_status:
        text_captcha = "🟢 ВЫКЛЮЧИТЬ КАПЧУ"
    else:
        text_captcha = "🔴 ВКЛЮЧИТЬ КАПЧУ"
    settings_menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=text_captcha,
                                callback_data="captcha_edit")
        ],
        [
            InlineKeyboardButton(text="👈 НАЗАД", callback_data="admin")
        ]
    ])
    await state.set_state(AdminStates.settings)
    await callback_query.answer()
    await bot.edit_message_text(text='<b>⚙️ Настройки</b>', reply_markup=settings_menu, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@any_admin_router.callback_query(F.data == 'captcha_edit', StateFilter(AdminStates.settings))
async def captcha_edit_function(callback_query: CallbackQuery, state: FSMContext):
    captcha_status = await MainGets().captcha_status()
    if captcha_status:
        await Admins().update_captcha_status(False)
        text_captcha = "🔴 ВКЛЮЧИТЬ КАПЧУ"
    else:
        await Admins().update_captcha_status(True)
        text_captcha = "🟢 ВЫКЛЮЧИТЬ КАПЧУ"
    settings_menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=text_captcha,
                                 callback_data="captcha_edit")
        ],
        [
            InlineKeyboardButton(text="👈 НАЗАД", callback_data="admin")
        ]
    ])
    await state.set_state(AdminStates.settings)
    await callback_query.answer()
    await bot.edit_message_text(text='<b>⚙️ Настройки</b>', reply_markup=settings_menu, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
