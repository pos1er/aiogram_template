import ast
import math
import aiohttp
from abc import _P
from typing import Dict, List, Union
from aiogram.utils.i18n import gettext as _
from aiogram.types import InputMediaPhoto, InputMediaVideo

from bot.data.config import DEFAULT_LANGUAGE
from bot.loader import bot
from mongodb.mongodb import counters, db_data, admins


async def get_accept_languages() -> List[str]:
        languages = db_data.find_one(
            {'id': 1}, {'_id': False, 'languages': True})['languages']
        return [lang['code'] for lang in languages if lang['status']]


async def get_id_database(database: str) -> int:
    return counters.find_one_and_update({'id': 1}, {'$inc': {database: 1}}, {'_id': False, database: True}, return_document=True)[database]


async def add_available_languages(languages: Dict[str, str], my_language: str):
    main_language = DEFAULT_LANGUAGE
    available_languages = await get_accept_languages()
    if main_language in languages:
        main_text = languages[main_language]
    elif my_language in languages:
        main_text = languages[my_language]
    else:
        main_text = list(languages.values())[0]
    for language in available_languages:
        if language not in languages:
            languages[language] = main_text
    return languages
        

async def hours_text(hour: float):
    hour = math.ceil(hour)
    hours = [0, 5, 6, 7, 8, 9]
    if hour % 10 in hours or (hour % 100) // 10 == 1:
        data = _('часов')
    elif hour % 10 == 1:
        data = _('час')
    else:
        data = _P('часа')
    return data


async def minutes_text(minute: float):
    minute = math.ceil(minute)
    minutes = [0, 5, 6, 7, 8, 9]
    if minute % 10 in minutes or (minute % 100) // 10 == 1:
        data = _('минут')
    elif minute % 10 == 1:
        data = _('минута')
    else:
        data = _('минуты')
    return data


def round_down(n: Union[float, int], decimals: int = 0) -> Union[float, int]:
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


async def int_to_asset(number: Union[int, float], asset: str, asset_to: str = 'RUB', rates: Union[Dict, None] = None) -> Union[int, float]:
    if asset == asset_to:
        return number
    if asset != "RUB":
        new_number = round_down(number / await currencies_price_rub(asset, rates), 2)
    else:
        new_number = round_down(number * await currencies_price_rub(asset_to, rates), 2)
    if asset == "RUB" or asset_to == "RUB":
        return new_number
    else:
        return round_down(new_number * await currencies_price_rub(asset_to, rates), 2)


async def currencies_price_rub(currency: str, rates: Union[Dict, None] = None) -> Union[float, int]:
    if not rates:
        rates = db_data.find_one({'id': 1}, {'_id': False, 'rates': True})['rates']
    return rates[currency]


async def currencies_price_rub_request() -> None:
    session = aiohttp.ClientSession()
    response = await session.get('https://www.cbr-xml-daily.ru/latest.js')
    async with session as close_session: pass
    rates = ast.literal_eval(await response.text())
    db_data.update_one({'id': 1}, {'$set': {'rates': rates['rates']}})


async def cryptocurrencies_price(cryptocurrency, currency):
    if cryptocurrency == "USDT" and currency == "USD":
        return 1
    elif cryptocurrency == "USDT" and currency == "EUR":
        currency, cryptocurrency = cryptocurrency, currency
    elif cryptocurrency == "BTC" and currency == "USD":
        currency = "USDT"
    session = aiohttp.ClientSession()
    response = await session.get(f"https://api.binance.com/api/v3/ticker/price?symbol={cryptocurrency}{currency}")
    data = await response.json()
    async with session as close_session: pass
    if currency == "USDT" and cryptocurrency == "EUR":
        return 2 - float(data['price'])
    return data['price']


async def get_full_name(chat_id: int) -> str:
    info = await bot.get_chat_member(chat_id, chat_id)
    return info.user.full_name


async def get_username(chat_id: int) -> Union[None, str]:
    info = await bot.get_chat_member(chat_id, chat_id)
    return info.user.username


async def get_bot_username() -> Union[None, str]:
    info = await bot.get_me()
    return info.username


def admin_id_by_chat_id(chat_id: int) -> Union[None, int]:
    return admins.find_one({'user_id': chat_id}, {'_id': False, 'id': True})['id']


async def admin_chat_id_by_id(admin_id: int) -> Union[int, str]:
    user_id = admins.find_one(
        {'id': admin_id}, {'_id': False, 'user_id': True})
    if user_id:
        return user_id['user_id']
    else:
        return 'none'


async def to_usdt(currency, rates, amount):
    if currency == 'TRX':
        amount = round(amount * await Payments('crystal_pay').get_trx_crystal_pay())
    for rate in rates:
        if rate['target'] == 'RUB':
            return round(amount / float(rate['rate']), 2)

# ONLY PHOTO

async def media_group_from_list(list_photos, caption, parse_mode) -> List[InputMediaPhoto]:
    photo_list = []
    for photo in list_photos:
        if photo_list == [] and caption:
            photo_list.append(InputMediaPhoto(
                type='photo', media=photo, caption=caption, parse_mode=parse_mode))
        else:
            photo_list.append(InputMediaPhoto(
                type='photo', media=photo))
    return photo_list


async def all_media_group_from_list(list_files, caption, parse_mode) -> List[InputMediaPhoto]:
    files_list = []
    for file in list_files:
        if files_list == [] and caption:
            if file.type == 'photo':
                files_list.append(InputMediaPhoto(
                    type='photo', media=file.id, caption=caption, parse_mode=parse_mode))
            elif file.type == 'video':
                files_list.append(InputMediaVideo(
                    type='video', media=file.id, caption=caption, parse_mode=parse_mode))
        else:
            if file.type == 'photo':
                files_list.append(InputMediaPhoto(
                    type='photo', media=file.id))
            elif file.type == 'video':
                files_list.append(InputMediaVideo(
                    type='video', media=file.id))
    return files_list


async def languages_text_status(langs) -> str:
    languages = db_data.find_one({'id': 1}, {'_id': False, 'languages': True})['languages']
    text = ''
    for lang in languages:
        if lang['status']:
            text += f'{lang["text"]} — {"✅" if lang["code"] in langs else "❌"}\n'
    return text + '\n'


async def get_count_languages() -> int:
    return len(db_data.find_one({"id": 1}, {"_id": False, "languages": True})["languages"])


async def int_check(data, int_num_max=None, int_num_min=None):
    if not data.isdigit():
        return _('<b>❗️ Ошибка: Введите число</b>')
    if int_num_max:
        if int(data) > int_num_max:
            return _('<b>❗️ Ошибка: Число должно быть не больше {int_num_max}</b>').format(int_num_max=int_num_max)
    if int_num_min:
        if int(data) < int_num_min:
            return _('<b>❗️ Ошибка: Число должно быть не меньше {int_num_min}</b>').format(int_num_min=int_num_min)
    return 'confirm'


async def money_currency_check(money, currency, currency_symbol, rub_max, rub_min):
    max_currency = await int_to_asset(rub_max, "RUB", currency)
    min_currency = await int_to_asset(rub_min, "RUB", currency)
    if money > max_currency:
        return _('<b>❗️ Ошибка: Число должно быть не больше</b> <code>{int_num_max}{currency_symbol}</code>').format(int_num_max=max_currency, currency_symbol=currency_symbol)
    if money < min_currency:
        return _('<b>❗️ Ошибка: Число должно быть не меньше</b> <code>{int_num_min}{currency_symbol}</code>').format(int_num_min=min_currency, currency_symbol=currency_symbol)
    return 'confirm'