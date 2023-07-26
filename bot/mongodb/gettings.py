import datetime
from typing import List
from mongodb.mongodb import db_data, admins, users, admins_requests


async def get_faq():
        return db_data.find_one({'id': 1}, {'_id': False, 'faq_text': True})['faq_text']


async def captcha_status():
    return db_data.find_one({'id': 1})['captcha_status']


async def get_admins_list(selection: str = 'status') -> List:
    return list(admins.find({selection: True}, {'_id': False, 'user_id': True}))


async def booking_status():
    return db_data.find_one({'id': 1})['booking_status']


async def tm_status():
    return db_data.find_one({'id': 1}, {'_id': False, 'tm_status': True})['tm_status']


async def tm_status_and_ban(user_id: int) -> bool:
    data = db_data.find_one({'id': 1}, {'_id': False, 'users_block': True, 'tm_status': True, 'admins_forever': True})
    tm_status = data['tm_status']
    user_ban = True if user_id in data['users_block'] else False
    user_admin = True if user_id in data['admins_forever'] else False
    return True if (not user_ban and not tm_status) or user_admin else False


async def get_language(user_id) -> str:
    return users.find_one({'user_id': user_id}, {'_id': False, 'language': True})['language']


async def get_picture(picture_id: str):
    pics = db_data.find_one({'id': 1, f'pictures.{picture_id}': {'$type': 'string'}}, {f'pictures.{picture_id}': True, '_id': False})
    if pics:
        pics = pics['pictures'][picture_id]
    return pics


async def check_admin_request(code):
    try:
        time_access = admins_requests.find_one(
            {'code': code}, {'_id': False, 'time_access': True})['time_access']
        return admins_requests.find_one({'code': code, 'timestamp': {'$gte': datetime.datetime.utcnow().timestamp() - time_access},
                                            'left': {'$gte': 1}})
    except TypeError:
        pass
