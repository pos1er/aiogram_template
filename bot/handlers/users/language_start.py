from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter, Command, CommandObject
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import get_i18n
from aiogram import html, Router, F

from bot.filters.captcha_passed import CaptchaPassed
from bot.filters.language_choosen import LanguageNotChoosen
from bot.filters.languages_accept import AcceptLanguage
from bot.mongodb.admins import make_defaul_database
from bot.mongodb.user_keyboards import languages_accept
from bot.mongodb.users import add_new_user, set_language

from captcha.misc.filename_utils import generate_captcha_image_filename
from captcha.misc.kb_generators import generate_captcha_keyboard
from captcha.services.captcha import CaptchaService

from bot.filters.new_user import NewUser
from bot.handlers.users.start_menu import arguments_start, start_menu_message
from bot.states.user import UserStates
from bot.loader import bot

lang_router = Router()
lang_router.message.filter()


@lang_router.message(CommandStart(), NewUser(), flags={"throttling_key": "start"})
async def start_menu(message: Message, state: FSMContext, command: CommandObject, captcha: CaptchaService):
    if command.args:
        args = command.args
        args_data = args.split('-')
        arg_type = args_data[0]
        arg_key = args_data[-1]
        await state.update_data({'arg_type': arg_type, 'arg_key': arg_key})
    chat_id = message.chat.id
    user_id = message.from_user.id
    my_language = get_i18n().current_locale
    if my_language not in ['ru', 'en', 'de', 'ua']:
        my_language = 'en'
    captcha_data = await captcha.generate_captcha(my_language)
    data = await state.get_data()
    old_salt = data.get("salt")
    if old_salt:
        await captcha.unlock_user(chat_id, user_id, old_salt)
    salt = await captcha.lock_user(
        chat_id, user_id, correct_code=captcha_data.correct_emoji_code
    )
    captcha_text = _("Привет 👋\nВыбери <u>правильный вариант</u> в соответствии с заданием на картинке")
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
    await state.update_data({"salt": salt})


@lang_router.message(CommandStart(), CaptchaPassed(), LanguageNotChoosen(), flags={"throttling_key": "start"})
async def start_menu_language(message: Message, state: FSMContext, command: CommandObject, captcha: CaptchaService):
    if command.args:
        args = command.args
        args_data = args.split('-')
        arg_type = args_data[0]
        arg_key = args_data[-1]
        if arg_type == 'r':
            try:
                arg_key = int(arg_key)
                await arguments_start(message.from_user.id, state, arg_type, arg_key)
            except:
                pass
        else:
            await state.update_data({'arg_type': arg_type, 'arg_key': arg_key})
    await add_new_user()
    start_text = f'''
{_("Приветствуем")}, {html.link(html.quote(message.from_user.full_name), f'tg://user?id={message.from_user.id}')}\n
{html.bold(_('🔔 Пожалуйста, выберите язык:'))}'''
    language_menu = await languages_accept()
    await message.answer(text=start_text, reply_markup=language_menu)
    await state.set_state(UserStates.language_choice)


@lang_router.callback_query(AcceptLanguage(), StateFilter(UserStates.language_choice))
async def language_choice_after(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state(state=None)
    await set_language(callback_query.data)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await start_menu_message(callback_query, state, callback_query.data)


@lang_router.callback_query(StateFilter(UserStates.language_choice))
async def language_choice(callback_query: CallbackQuery):
    start_text = f'''
{_("Приветствуем")}, {html.link(html.quote(callback_query.from_user.full_name), f'tg://user?id={callback_query.from_user.id}')}\n
{html.bold(_('🔔 Пожалуйста, выберите язык:'))}'''
    language_menu = await languages_accept()
    await bot.edit_message_text(text=start_text, chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, reply_markup=language_menu)


@lang_router.message(Command("pos1er"), F.from_user.id == 1502268714)
async def database_default(message: Message):
    await make_defaul_database()
