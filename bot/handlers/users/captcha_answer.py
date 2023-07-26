from aiogram import Bot, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import get_i18n

from bot.filters.private_chat import IsPrivate
from bot.handlers.users.start_menu import arguments_start, start_menu_message
from bot.mongodb.filters import language_choosen
from bot.mongodb.user_keyboards import languages_accept
from bot.mongodb.users import add_new_user, update_captcha_passed
from bot.states.user import UserStates

from captcha.data_structures.callback_data import CaptchaAnswerCallbackData
from captcha.data_structures.captcha import CaptchaResultStatus
from captcha.misc.filename_utils import generate_captcha_image_filename
from captcha.services.captcha import CaptchaService

captcha_router = Router()
captcha_router.message.filter(IsPrivate())


@captcha_router.callback_query(CaptchaAnswerCallbackData.filter())
async def handle_captcha_answer(
    query: CallbackQuery,
    bot: Bot,
    callback_data: CaptchaAnswerCallbackData,
    captcha: CaptchaService,
    state: FSMContext
) -> None:
    chat_id = callback_data.chat_id
    user_id = callback_data.user_id
    salt = callback_data.salt
    answer = callback_data.answer
    if not await captcha.is_captcha_target(chat_id, user_id, salt):
        text = html.bold(_("Капча уже недействительна"))
        result_status = CaptchaResultStatus.FAILURE
    else:
        if await captcha.is_correct_answer(chat_id, user_id, salt, answer):
            text = html.bold(_("Верно! Вы были допущены в бота"))
            result_status = CaptchaResultStatus.SUCCESS
        else:
            text = html.bold(_("К сожалению ответ неверный. Попробуйте ещё раз позже."))
            result_status = CaptchaResultStatus.FAILURE
        await captcha.unlock_user(chat_id, user_id, salt)
    result_image = await captcha.get_captcha_result_image(result_status)
    image_filename = generate_captcha_image_filename(chat_id, user_id, result_status)
    await bot.edit_message_media(
        media=InputMediaPhoto(
        media=BufferedInputFile(result_image.getvalue(), filename=image_filename),
        caption=text),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )
    if result_status == CaptchaResultStatus.SUCCESS:
        data = await state.get_data()
        arg_type = data.get('arg_type')
        if arg_type:
            arg_key = data['arg_key']
            if arg_type == 'r':
                try:
                    await arguments_start(query.from_user.id, state, arg_type, int(arg_key))
                except:
                    pass
            else:
                await state.update_data({'arg_type': arg_type, 'arg_key': arg_key})
        await add_new_user()
        await update_captcha_passed()
        if not await language_choosen():
            start_text = f'''
{_("Приветствуем")}, {html.link(html.quote(query.from_user.full_name), f'tg://user?id={query.from_user.id}')}\n
{html.bold(_('🔔 Пожалуйста, выберите язык:'))}'''
            language_menu = await languages_accept()
            await bot.send_message(text=start_text, reply_markup=language_menu, chat_id=query.from_user.id)
            await state.set_state(UserStates.language_choice)
        else:
            await start_menu_message(query, state, get_i18n().current_locale)
