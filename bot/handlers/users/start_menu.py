import datetime
from typing import Union
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import get_i18n
from aiogram import html, Router, F

from bot.filters.admins import AdminFilter
from bot.filters.private_chat import IsPrivate
from bot.handlers.admins.any_admin import notification
from bot.keyboards.inline.user import profile_keyboard,  delete_me
from bot.keyboards.default.user import start_menu_keyboard
from bot.keyboards.default.admin import start_admin_menu_keyboard
from bot.mongodb.admin_keyboards import admin_main_menu
from bot.mongodb.admins import update_tm_status
from bot.mongodb.filters import admin_check
from bot.mongodb.gettings import check_admin_request, get_picture, tm_status
from bot.mongodb.users import accept_admin_request, add_new_user
from bot.states.admin import AdminStates
from bot.loader import bot

start_router = Router()
start_router.message.filter(IsPrivate())


async def arguments_start(user_id: int, state: FSMContext, arg_type: str, arg_key: Union[str, int], show_start: Union[Message, bool] = False):
    if arg_type == 'admin':
        if not await admin_check(''):
            if await check_admin_request(arg_key):
                await add_new_user()
                full_name = await accept_admin_request(arg_key)
                await state.clear()
                await bot.send_message(chat_id=user_id, text=_("<b>✅ Клавиатура изменена</b>"), reply_markup=start_admin_menu_keyboard())
                text_menu = _(
                    "🔸 <b><u>Вход прошел успешно</u></b>\n\n<b>Добро пожаловать, {}</b>").format(html.link(html.quote(full_name),
                                                                                                           f"tg://user?id={user_id}"))
                await state.set_state(AdminStates.admin)
                admin_menu = await admin_main_menu()
                await bot.send_message(text=text_menu, reply_markup=admin_menu, chat_id=user_id)
                return True
    else:
        if isinstance(show_start, Message):
            await start_menu_message(show_start, state, get_i18n().current_locale)
    await state.update_data({'arg_key': None, 'arg_type': None})


async def start_menu_message(update: Union[Message, CallbackQuery], state: FSMContext, locale: str):
    data = await state.get_data()
    return_start = False
    if data.get('arg_type') and data.get('arg_key'):
        return_start = await arguments_start(update.from_user.id, state, data['arg_type'], data['arg_key'])
    keyboard = start_menu_keyboard(locale)
    if await admin_check(''):
        keyboard = start_admin_menu_keyboard(locale)
    start_text = _('<b>🎗 Добро пожаловать, {full_name}!</b>', locale=locale).format(
        full_name=html.link(html.quote(update.from_user.full_name),
                            f"tg://user?id={update.from_user.id}"))
    pic_start = await get_picture('start')
    if pic_start:
        msg = await bot.send_photo(photo=pic_start, caption=start_text, reply_markup=keyboard, chat_id=update.from_user.id)
    else:
        msg = await bot.send_message(text=start_text, reply_markup=keyboard, chat_id=update.from_user.id)
    if return_start:
        await bot.delete_message(chat_id=update.from_user.id, message_id=msg.message_id)


@start_router.message(Command('stop'), AdminFilter('main_admin'))
async def stop_bot_func(message: Message, state: FSMContext):
    status = await tm_status()
    if status:
        await update_tm_status(False)
    else:
        await update_tm_status(True)


@start_router.message(CommandStart(magic=F.args), flags={"throttling_key": "start"})
async def start_menu_with_arguments(message: Message, state: FSMContext, command: CommandObject):
    args = command.args
    args_data = args.split('-')
    arg_type = args_data[0]
    arg_key = args_data[-1]
    await arguments_start(message.from_user.id, state, arg_type, arg_key, message)


@start_router.message(CommandStart(), flags={"throttling_key": "start"})
async def start_menu_func(message: Message, state: FSMContext):
    await state.clear()
    await start_menu_message(message, state, get_i18n().current_locale)
