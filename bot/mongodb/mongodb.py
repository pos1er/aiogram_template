from aiogram.types import User
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import get_i18n
from pymongo import MongoClient
from bot.data.config import MONGODB_URL

mdb = MongoClient(MONGODB_URL)
db = mdb.get_database()
counters = db["counters"]
db_data = db["db_data"]
admins = db["admins"]
users = db["users"]
payments = db["payments"]
withdraws_db = db["withdraws_db"]
admins_requests = db["admins_requests"]

user = User.get_current()
user_id = user.id
username = user.username
full_name = user.full_name
