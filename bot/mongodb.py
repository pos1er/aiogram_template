import datetime
import io
from typing import Coroutine
from xmlrpc.client import Boolean

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, User
from pymongo import MongoClient
from bot.data.config import mongodb_url, crystal_pay_key, crypto_bot_key, private_key_payid19, public_key_payid19
import time
import aiohttp
import json

mdb = MongoClient(mongodb_url)
db_data = mdb.get_database()["db_data"]
admins = mdb.get_database()["admins"]
users = mdb.get_database()["users"]
payments = mdb.get_database()["payments"]


class Users:
    def __init__(self) -> None:
        user = User.get_current()
        self.user_id = user.id
        self.username = user.username
        self.full_name = user.full_name

    async def add_new_user(self) -> Boolean:
        table = users.find_one({'user_id': self.user_id}, {'_id': False, 'user_id': True})
        if not table:
            table = {
                "user_id": self.user_id,
                "username": self.username,
                "language": 'en',
                "time_reg": time.time()
            }
            users.insert_one(table)
            return True
        else:
            return False
    
    async def set_language(self, language) -> None:
        users.update_one({'user_id': self.user_id}, {'$set': {'language': language}})

class Payments:
    def __init__(self, amount, payment_id, payment_system, bot_username) -> None:
        user = User.get_current()
        self.user_id = user.id
        self.amount = amount
        self.payment_id = payment_id
        self.payment_system = payment_system
        self.bot_username = bot_username
    
    async def new_payment(self, *args):
        requests_count = list(payments.find({}, {'_id': False, 'id': True}).sort([
            ('$natural', -1)]).limit(1))
        try:
            request_num = requests_count[0]['id'] + 1
        except:
            request_num = 1
        payment_data = {
            'id': request_num,
            'user_id': self.user_id,
            'amount': self.amount,
            'payment_system': self.payment_system,
            'payment_system_id': request_num,
            'status': 'waiting',
            'timestamp': time.time()
        }
        if self.payment_system == 'payid19':
            payment_system_id, payment_url = await self.new_payid19(request_num)
        elif self.payment_system == 'crystal_pay':
            payment_system_id, payment_url = await self.new_crystal_pay()
        elif self.payment_system == 'crypto_bot':
            payment_system_id, payment_url = await self.new_crypto_bot(request_num, *args)
        else: return None
        if payment_url:
            payment_data['payment_system_id'] = payment_system_id
            payments.insert_one(payment_data)
            users.update_one({'user_id': self.user_id}, {
                '$set': {'payment_id': request_num, 'payment_system': self.payment_system}})
            return payment_system_id, payment_url
    
    async def check_payment(self):
        user_data = None
        if self.payment_system == 'payid19':
            answer, user_data = await self.check_payid19()
        elif self.payment_system == 'crystal_pay':
            answer = await self.check_crystal_pay()
        elif self.payment_system == 'crypto_bot':
            answer = await self.check_crypto_bot()
        else: return None
        if user_data:
            payments.update_one({'payment_id': self.payment_id}, {'$set': {'status': 'payed', 'ip': user_data['ip'], 'email': user_data['email']}})
            users.update_one({'user_id': self.user_id}, {
                             '$set': {'ip': user_data['ip'], 'email': user_data['email']}})
        elif answer:
            payments.update_one({'payment_id': self.payment_id}, {'$set': {'status': 'payed'}})
        return True
    
    async def new_crypto_bot(self, request_num, asset):
        asset = asset.upper()
        amount_value = round(self.amount / float(await Utils().cryptocurrencies_price(asset, 'RUB')), 15)
        print(amount_value)
        headers = {
            'Crypto-Pay-API-Token': crypto_bot_key
        }
        session = aiohttp.ClientSession(headers=headers)
        request_data = {
            'asset': asset,
            'amount': amount_value,
            'description': f'#{request_num} | Пополнение баланса @{self.bot_username} для ID[{self.user_id}]',
            'hidden_message': 'Спасибо за оплату!'
        }
        response = await session.post('https://pay.crypt.bot/api/createInvoice', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if data['ok']:
            return data['result']['invoice_id'], data['result']['pay_url']
        else:
            return request_num, False
    
    async def new_payid19(self, request_num):
        request_data = {
            'private_key': private_key_payid19,
            'public_key': public_key_payid19,
            'price_amount': self.amount,
            'price_currency': 'RUB',
            'costumer_id': self.user_id,
            'order_id': request_num,
            'title': f'Пополнение баланса @{self.bot_username} для ID[{self.user_id}]',
            'description': f'Ваш номер платежа - {request_num}',
            'mirgin_ratio': 0.5
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://payid19.com/api/v1/create_invoice', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if data['status'] == 'success':
            return request_num, data['message']
        else:
            return request_num, False

    async def new_crystal_pay(self):
        site_redirect = f'https://t.me/{self.bot_username}'
        session = aiohttp.ClientSession()
        response = await session.get(f'https://api.crystalpay.ru/v1/?s={crystal_pay_key}&n=pos1er&o=invoice-create&amount={self.amount}&currency=RUB&redirect={site_redirect}')
        data = await response.json()
        async with session as close_session: pass
        payment_id = data['id']
        url_user = data['url']
        if url_user:
            return payment_id, url_user
        else:
            return payment_id, False

    async def check_crystal_pay(self):
        session = aiohttp.ClientSession()
        response = await session.get(f'https://api.crystalpay.ru/v1/?s={crystal_pay_key}&n=pos1er&o=invoice-check&i={payment_id}')
        data = await response.json()
        async with session as close_session: pass
        if data['state'] == 'payed':
            return True
    
    async def check_payid19(self):
        request_data = {
            'private_key': private_key_payid19,
            'public_key': public_key_payid19,
            'order_id': self.payment_id
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://payid19.com/api/v1/get_invoices', data=request_data)
        data = await response.json()
        json_data = json.loads(data['message'])
        async with session as close_session: pass
        if json_data:
            return True, json_data[0]
        else:
            return False, None
    
    async def check_crypto_bot(self):
        headers = {
            'Crypto-Pay-API-Token': crypto_bot_key
        }
        session = aiohttp.ClientSession(headers=headers)
        request_data = {
            'offset': 0,
            'count': 100,
            'invoice_ids': str(self.payment_id)
        }
        response = await session.post('https://pay.crypt.bot/api/getInvoices', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if data['result']['items']:
            return True, data[0]
        else:
            return False, None


class ForFilters:
    def __init__(self) -> None:
        user = User.get_current()
        self.user_id = user.id

    async def admin_check(self, admin_right) -> Coroutine:
        if admin_right:
            return admins.find_one({'user_id': self.user_id, f'rights.{admin_right}': True})
        else:
            return admins.find_one({'user_id': self.user_id})
    
    async def user_check(self, user_id) -> Coroutine:
        #  todo: сделать блок по времени
        return users.find_one({'user_id': user_id, 'block': True, 'bot_accept': True}, {'_id': False, 'block': True})

    async def get_language(self) -> Coroutine:
        return users.find_one({'user_id': self.user_id}, {'_id': False, 'language': True})
    
    async def old_user(self) -> Coroutine:
        return users.find_one({'user_id': self.user_id}, {'_id': False, 'user_id': True})


class Admins:
    def __init__(self) -> None:
        user = User.get_current()
        self.user_id = user.id

    async def make_defaul_database(self) -> None:
        admin = {
            'user_id': self.user_id,
            'type': 'main_admin',
            'name': '🅰️ Админ',
            'time': time.time()
        }
        admins.drop()
        admins.insert_one(admin)
        data = {
            'id': 1,
            'captcha_status': False,
            'languages': ['ru', 'en', 'de'],
            'rights': []
        }
        db_data.drop()
        db_data.insert_one(data)
    
    async def update_captcha_status(self, new_status):
        db_data.update_one({'id': 1}, {'$set': {'captcha_status': new_status}})


class Utils:
    @staticmethod
    async def cryptocurrencies_price(cryptocurrency, currency):
        session = aiohttp.ClientSession()
        response = await session.get(f"https://api.binance.com/api/v3/ticker/price?symbol={cryptocurrency}{currency}")
        data = await response.json()
        async with session as close_session: pass
        return data['price']

class ErrorsCheck:
    ...

class Timers:
    ...

class Keyboards:
    ...

class MainGets:
    async def captcha_status(self):
        return db_data.find_one({'id': 1})['captcha_status']

class MainEdits:
    ...
