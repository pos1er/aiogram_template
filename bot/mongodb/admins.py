import datetime
from bot.mongodb.utils import get_id_database
from mongodb.mongodb import admins, db_data, user_id
import time


async def make_defaul_database() -> None:
    admin = {
        'user_id': user_id,
        'type': 'main_admin',
        'name': '🅰️ Админ',
        'rights': {},
        'notifications': {'daily': True},
        'status': True,
        'time': time.time()
    }
    admins.drop()
    admins.insert_one(admin)
    data = {
        'id': 1,
        'captcha_status': False,
        'languages': ['ru', 'en', 'de', 'ua'],
        'rights': []
    }
    db_data.drop()
    db_data.insert_one(data)


async def add_waiting_chat(message_id):
    admins.update_one({'user_id': user_id}, {'$set': {'waiting_chat': message_id}})


async def get_waiting_chat():
    return admins.find_one({'user_id': user_id}, {'_id': False, 'waiting_chat': True})['waiting_chat']


async def clear_waiting_chat():
    admins.update_one({'user_id': user_id}, {'$unset': {'waiting_chat': 1}})


async def admins_list(right=None, notification=None):
    if right:
        return admins.find({f'rights.{right}': True})
    elif notification:
        return admins.find({f'notifications.{notification}': True})
    else:
        return admins.find({})


async def update_captcha_status(new_status):
    db_data.update_one({'id': 1}, {'$set': {'captcha_status': new_status}})


async def update_tm_status(new_status):
    db_data.update_one({'id': 1}, {'$set': {'tm_status': new_status}})


async def update_booking_status(new_status):
    db_data.update_one({'id': 1}, {'$set': {'booking_status': new_status}})


async def add_admin(admin_id, admin_invite, admin_type, rights=None, notifications=None):
    if not rights:
        rights = dict.fromkeys(db_data.find_one({'id': 1}, {'_id': None, 'rights': True})['rights'], False)
    if not notifications:
        notifications = dict.fromkeys(db_data.find_one(
            {'id': 1}, {'_id': None, 'notifications': True})['notifications'], False)
    table = admins.find_one({'user_id': admin_id})
    if not table:
        id_admin = await get_id_database('admins')
        table = {
            "id": id_admin,
            "user_id": admin_id,
            "admin_invite": admin_invite,
            "type": admin_type,
            "rights": rights,
            "notifications": notifications,
            "status": True,
            "timestamp": datetime.datetime.utcnow().timestamp()
        }
        admins.insert_one(table)