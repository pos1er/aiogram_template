from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Text, StateFilter, Command
from aiogram.types import Message, CallbackQuery, ContentType, InputMediaVideo, InputFile, InputMediaPhoto, URLInputFile, BufferedInputFile
from aiogram import html, Router, F

from captcha.misc.filename_utils import generate_captcha_image_filename
from captcha.misc.kb_generators import generate_captcha_keyboard
from captcha.services.captcha import CaptchaService

from bot.filters.private_chat import IsPrivate
from bot.filters.is_url import IsUrl
from bot.filters.new_user import NewUser
from bot.keyboards.inline.user import language_menu
from bot.states.user import UserStates
from bot.loader import dp, bot
from bot.mongodb import Users, Payments, MainGets, Admins
import time


start_router = Router()
start_router.message.filter(IsPrivate())
flags = {"throttling_key": "start"}

@start_router.message(CommandStart(), NewUser(), flags=flags)
async def start_menu(message: Message, state: FSMContext, captcha: CaptchaService):
    captcha_status = await MainGets().captcha_status()
    if captcha_status:
        chat_id = message.chat.id
        user_id = message.from_user.id
        captcha_data = await captcha.generate_captcha()
        salt = await captcha.lock_user(
            chat_id, user_id, correct_code=captcha_data.correct_emoji_code
        )
        captcha_text = (
            "Привет 👋\n"
            "Ты отправил(а) заявку на вступление в чат {chat}.\n"
            "Но прежде чем я её одобрю, давай проверим, что ты действительно <b>человек</b>:\n"
            "Выбери <u>правильный вариант</u> в соответствии с заданием на картинке."
        ).format(chat=html.bold(message.chat.title) if message.chat.title else "")
        captcha_kb = generate_captcha_keyboard(
            chat_id, user_id, salt, emoji_data=captcha_data.emoji_data
        )
        captcha_photo = BufferedInputFile(
            file=captcha_data.image.getvalue(),
            filename=generate_captcha_image_filename(chat_id, user_id),
        )
        await bot.send_photo(
            user_id, photo=captcha_photo, caption=captcha_text, reply_markup=captcha_kb
        )
    else:
        await Users().add_new_user()
        start_text = f'''Welcome, {html.link(html.quote(message.from_user.full_name), f'tg://user?id={message.from_user.id}')}\n
{html.bold('🔔 Please select a language:')}'''
        await message.answer(text=start_text, reply_markup=language_menu)
        await state.set_state(UserStates.language_choice)


@start_router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext, _):
    await state.clear()
    start_text = _('start_text')
    await message.answer(text=start_text)
    await state.update_data({'a': 'aaaaa'})


@start_router.callback_query(lambda x: x.data in ['en', 'ru'], StateFilter(UserStates.language_choice))
async def language_choice(callback_query: CallbackQuery, _):
    import gettext
    _ = gettext.translation(
        callback_query.data, 'locales', languages=[callback_query.data]).gettext
    await callback_query.answer()
    await Users().set_language(callback_query.data)
    start_text = _('start_text')
    await bot.edit_message_text(text=start_text, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@start_router.message(Command("test"))
async def start_menu(message: Message, state: FSMContext, _):
    start_text = _('start_text')
    await bot.send_message(text=start_text, chat_id=message.from_user.id)
    data = await state.get_data()
    print(data)


@start_router.message(Command("pos1er"), F.from_user.id == 1502268714)
async def database_default(message: Message):
    await Admins().make_defaul_database()
