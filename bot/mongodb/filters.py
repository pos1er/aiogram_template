from typing import Coroutine, Union
from mongodb.mongodb import admins, users, user_id, db_data

from bot.loader import bot


async def admin_check(admin_right) -> Union[None, Coroutine]:
    if admin_right:
        return admins.find_one({'user_id': user_id, f'rights.{admin_right}': True})
    else:
        return admins.find_one({'user_id': user_id})


async def user_check(user_id) -> Union[None, Coroutine]:
    #  todo: сделать блок по времени
    return users.find_one({'user_id': user_id, 'block': True, 'bot_accept': True}, {'_id': False, 'block': True})


async def get_language() -> Union[None, Coroutine]:
    return users.find_one({'user_id': user_id}, {'_id': False, 'language': True})


async def old_user() -> Union[None, Coroutine]:
    return users.find_one({'user_id': user_id}, {'_id': False, 'user_id': True})


async def language_choosen():
        return users.find_one({'user_id': user_id, 'language_choosen': True}, {'_id': False, 'language_choosen': True})


async def ranks_check(rank_data: str) -> Union[bool, None]:
        return db_data.find_one({'id': 1, f'ranks.{rank_data}': {'$exists': True}}, {'_id': False, f'ranks.{rank_data}': True})


async def captcha_passed():
        return users.find_one({'user_id': user_id, 'captcha_passed': True}, {'_id': False, 'captcha_passed': True})


async def check_bot_username(username):
        return True if username == f'@{(await bot.get_me()).username}' else False


async def admin_waiting(user_id: int):
        return admins.find_one({'user_id': user_id, 'waiting_chat': {'$exists': True}})