from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Text, StateFilter
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaVideo, InputFile, InputMediaPhoto, URLInputFile, BufferedInputFile
from aiogram import html, Router

from filters.private_chat import IsPrivate
from filters.is_url import IsUrl
from keyboards.inline.user import language_menu
from states.user import UserStates
from loader import dp, bot
from mongodb import Users
import time


router = Router()
router.message.filter(IsPrivate())


@router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext):
    await state.clear()
    await Users().add_new_user()
    start_text = f'''Welcome, {html.link(html.quote(message.from_user.full_name), f'tg://user?id={message.from_user.id}')}\n
{html.bold('🔔 Please select a language:')}'''
    await message.answer(text=start_text, reply_markup=language_menu)
    await state.set_state(UserStates.language_choice)


@router.callback_query(StateFilter(UserStates.language_choice))
async def language_choice(callback_query: CallbackQuery, state: FSMContext, _):
    await callback_query.answer()
    await Users().set_language(callback_query.data)
    start_text = _('start_text')
    await bot.edit_message_text(text=start_text, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.update_data({'language': callback_query.data})
