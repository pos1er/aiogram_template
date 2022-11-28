from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram import F, html, Router

from filters.private_chat import IsPrivate
from filters.admins import AdminFilter

from keyboards.inline.admin import admin_menu
from keyboards.inline.user import delete_me
from loader import dp, bot
from mongodb import Admins
from states.admin import AdminStates
from data.config import languages
import gettext


router = Router()
router.message.filter(IsPrivate(), AdminFilter())


# @dp.message(Command("admin"),
#                     AdminFilter())
# async def main_menu(message: Message):
#     await Admins().check_user_data()
#     start_text = f'Приветик, <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>!'
#     await message.answer(text=start_text, reply_markup=admin_menu)
#     await AdminStates.admin.set()


@dp.message(Command("pos1er"))
async def database_default(message: Message):
    await Admins().make_defaul_database()


@dp.message(Command("admin"))
async def database_default(message: Message, state: FSMContext):
    await state.clear()
    languages['ru'].install()
    _ = gettext.gettext
    text_menu = _('admin_start')
#     text_menu = f'''<u>Вход прошел успешно</u>\n
# <b>Добро пожаловать, {message.from_user.full_name}</b>'''
    await state.set_state(AdminStates.admin)
    await message.answer(text=text_menu, reply_markup=admin_menu)
        
