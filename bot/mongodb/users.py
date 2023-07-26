from bot.data.config import DEFAULT_LANGUAGE
from bot.mongodb.admins import add_admin
from bot.mongodb.mongodb import users, user_id, username, full_name, admins_requests
from bot.mongodb.utils import get_id_database
import time



async def add_new_user() -> bool:
    table = users.find_one({'user_id': user_id}, {'_id': False, 'user_id': True})
    if not table:
        num_id = await get_id_database('users')
        table = {
            "id": num_id,
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "language": DEFAULT_LANGUAGE,
            "time_reg": time.time()
        }
        users.insert_one(table)
        return True
    else:
        return False


async def set_language(language) -> None:
    users.update_one({'user_id': user_id}, {'$set': {'language': language}})


async def accept_admin_request(code):
    request = admins_requests.find_one(
        {'code': code}, {'left': True, '_id': False, 'admin_id': True})
    requests_left = request['left']
    invite_admin = request['admin_id']
    if requests_left <= 1:
        admins_requests.update_one({'code': code}, {'$inc': {'left': -1}, '$push': {'user_ids': user_id},
                                                    '$set': {'status': False}})
    else:
        admins_requests.update_one(
            {'code': code}, {'$inc': {'left': -1}, '$push': {'user_ids': user_id}})
    await add_admin(user_id, invite_admin, "admin")
    return full_name


async def update_captcha_passed():
        users.update_one({'user_id': user_id}, {'$set': {'captcha_passed': True}})