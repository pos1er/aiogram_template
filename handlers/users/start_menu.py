from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Text, StateFilter, Command
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaVideo, InputFile, InputMediaPhoto, URLInputFile, BufferedInputFile
from aiogram import html, Router

from app.misc.filename_utils import generate_captcha_image_filename
from app.misc.kb_generators import generate_captcha_keyboard
from app.services.captcha import CaptchaService

from filters.private_chat import IsPrivate
from filters.is_url import IsUrl
from filters.new_user import NewUser
from keyboards.inline.user import language_menu
from states.user import UserStates
from loader import dp, bot
from mongodb import Users, Payments, MainGets
import time


router = Router()
router.message.filter(IsPrivate())


@router.message(CommandStart(), NewUser())
async def start_menu(message: Message, state: FSMContext):
    captcha_status = await MainGets().captcha_status()
    if captcha_status:
        print(1)
        # captcha_data = await CaptchaService.generate_captcha()
        # salt = await CaptchaService.lock_user(
        #     chat_id, user_id, correct_code=captcha_data.correct_emoji_code
        # )
        # captcha_text = ("Привет 👋\n"
        #     "Выбери <u>правильный вариант</u> в соответствии с заданием на картинке.\n"
        #     "Hi 👋\n"
        #     "Choose the <u>right option</u> according to the task in the picture.")
        # captcha_kb = generate_captcha_keyboard(
        #     chat_id, user_id, salt, emoji_data=captcha_data.emoji_data
        # )
        # captcha_photo = BufferedInputFile(
        #     file=captcha_data.image.getvalue(),
        #     filename=generate_captcha_image_filename(chat_id, user_id),
        # )
        # await bot.send_photo(
        #     user_id, photo=captcha_photo, caption=captcha_text, reply_markup=captcha_kb
        # )
    else:
        await Users().add_new_user()
        start_text = f'''Welcome, {html.link(html.quote(message.from_user.full_name), f'tg://user?id={message.from_user.id}')}\n
{html.bold('🔔 Please select a language:')}'''
        await message.answer(text=start_text, reply_markup=language_menu)
        await state.set_state(UserStates.language_choice)


@router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext, _):
    await state.clear()
    start_text = _('start_text')
    await message.answer(text=start_text)


@router.callback_query(lambda x: x.data in ['en', 'ru'], StateFilter(UserStates.language_choice))
async def language_choice(callback_query: CallbackQuery, _):
    import gettext
    _ = gettext.translation(
        callback_query.data, 'locales', languages=[callback_query.data]).gettext
    await callback_query.answer()
    await Users().set_language(callback_query.data)
    start_text = _('start_text')
    await bot.edit_message_text(text=start_text, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@router.message(Command("test"))
async def start_menu(message: Message, _):
    start_text = _('start_text')
    await bot.send_message(text=start_text, chat_id=message.from_user.id)
