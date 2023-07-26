import datetime
import json
import aiohttp
import hashlib
from typing import Union
from dacite import from_dict
from aiogram.types import User
from aiogram.utils.i18n import gettext as _
from bot.data.payments import BalanceCryptobot, BalanceCrystalpay, BalancePayid19

from bot.mongodb.utils import cryptocurrencies_price, int_to_asset
from bot.data.config import BASE_URL
from mongodb.utils import get_id_database, get_bot_username
from mongodb.mongodb import payments, db_data, users, withdraws_db


class Payments:
    def __init__(self, payment_system: str, amount=None, payment_id=None, dont_check_id=False) -> None:
        user = User.get_current()
        if not dont_check_id:
            self.user_id = user.id
        self.amount = amount
        self.payment_id = payment_id
        self.payment_system = payment_system
        self.private_key = db_data.find_one({"id": 1}, {"_id": False, f"payment_systems.{self.payment_system}": True})['payment_systems'][self.payment_system]['private_key']
        self.public_key = None if self.payment_system not in ['payid19', 'crystal_pay'] else db_data.find_one(
            {"id": 1}, {"_id": False, f"payment_systems.{self.payment_system}": True})['payment_systems'][self.payment_system]['public_key']
    
    async def new_payment(self, asset="USDT", currency="RUB"):
        self.bot_username = await get_bot_username()
        request_num = await get_id_database('payments')
        payment_data = {
            'id': request_num,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': currency,
            'payment_system': self.payment_system,
            'payment_system_id': request_num,
            'status': 'waiting',
            'timestamp': datetime.datetime.utcnow().timestamp()
        }
        if self.payment_system == 'payid19':
            payment_system_id, payment_url = await self.new_payid19(request_num, currency)
        elif self.payment_system == 'crystal_pay':
            payment_system_id, payment_url = await self.new_crystal_pay()
        elif self.payment_system == 'qiwi':
            payment_system_id, payment_url = await self.new_qiwi(request_num, currency)
        elif self.payment_system == 'crypto_bot':
            payment_system_id, payment_url = await self.new_crypto_bot(request_num, asset, currency)
        else: return None, None
        if payment_url:
            payment_data['payment_system_id'] = payment_system_id
            payments.insert_one(payment_data)
            return request_num, payment_url
        else:
            return None, None
    
    async def check_webhook(self, check_data):
        if self.payment_system == 'payid19':
            return await self.webhook_payid19(check_data)
        elif self.payment_system == 'crystal_pay':
            return None
        elif self.payment_system == 'crypto_bot':
            return await self.webhook_crypto_bot(check_data)
        elif self.payment_system == 'qiwi':
            return await self.webhook_qiwi(check_data)
        else: return None
    
    async def webhook_payid19(self, check_data):
        if self.private_key == check_data:
            return True
    
    async def webhook_crypto_bot(self, check_data):
        #  todo сделать проверку, но там сложно...
        return True
    
    async def webhook_qiwi(self, check_data):
        if check_data == 'PAID':
            return True
    
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
            payments.update_one({'id': self.payment_id}, {'$set': {'status': 'payed', 'ip': user_data['ip'], 'email': user_data['email']}})
            users.update_one({'user_id': self.user_id}, {
                             '$set': {'ip': user_data['ip'], 'email': user_data['email']}})
        elif answer:
            payments.update_one({'id': self.payment_id}, {'$set': {'status': 'payed'}})
        return True
    
    async def new_crypto_bot(self, request_num, asset, currency):
        asset = asset.upper()
        amount_value = round(self.amount / float(await cryptocurrencies_price(asset, currency)), 15)
        headers = {
            'Crypto-Pay-API-Token': self.private_key
        }
        session = aiohttp.ClientSession(headers=headers)
        request_data = {
            'asset': asset,
            'amount': amount_value,
            'description': _('#{request_num} | Пополнение баланса @{bot_username} для ID[{user_id}]').format(request_num=request_num,
                                                                                                             bot_username=self.bot_username,
                                                                                                             user_id=self.user_id),
            'hidden_message': _('Спасибо за оплату!')
        }
        response = await session.post('https://pay.crypt.bot/api/createInvoice', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if data['ok']:
            return data['result']['invoice_id'], data['result']['pay_url']
        else:
            return request_num, False
    
    async def new_payid19(self, request_num, currency):
        request_data = {
            'private_key': self.private_key,
            'public_key': self.public_key,
            'price_amount': self.amount,
            'price_currency': currency,
            'costumer_id': self.user_id,
            'order_id': request_num,
            'title': _('Пополнение баланса @{bot_username} для ID[{user_id}]').format(bot_username=self.bot_username, user_id=self.user_id),
            'description': _('Ваш номер платежа - {request_num}').format(request_num=request_num),
            'mirgin_ratio': 0.5,
            'callback_url': f'{BASE_URL}/qshop-pay',
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://payid19.com/api/v1/create_invoice', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if data['status'] == 'success':
            return request_num, data['message']
        else:
            return request_num, False
    
    async def new_qiwi(self, request_num, currency):
        if currency != 'RUB':
            self.amount = await int_to_asset(self.amount, currency)
        request_data = {
            'token': self.private_key,
            'amount': self.amount,
            'order_id': request_num,
            'shop_id': 423
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://lk.rukassa.pro/api/v1/create', data=request_data)
        data = await response.json(content_type="text/html")
        async with session as close_session: pass
        if 'id' in data:
            return data['id'], data['url']
        else:
            return request_num, False

    async def new_crystal_pay(self):
        body = {
            'auth_login': 'pos1er',
            'auth_secret': self.public_key,
            'amount': self.amount,
            'type': 'topup',
            'description': _('Пополнение баланса @{bot_username} для ID[{user_id}]').format(bot_username=self.bot_username, user_id=self.user_id),
            'redirect_url': f'https://t.me/{self.bot_username}'
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://api.crystalpay.io/v2/invoice/create/', json=body)
        data = await response.json(content_type="text/html")
        async with session as close_session: pass
        payment_id = data['id']
        url_user = data['url']
        if url_user:
            return payment_id, url_user
        else:
            return payment_id, False

    async def check_crystal_pay(self):
        body = {
            'auth_login': 'pos1er',
            'auth_secret': self.public_key,
            'id': self.payment_id
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://api.crystalpay.io/v2/invoice/info/', json=body)
        data = await response.json(content_type="text/html")
        async with session as close_session:
            pass
        if not data['error']:
            errors = {'notpayed': 'Платеж не оплачен'}
            return data['balances']
    
    async def check_payid19(self):
        request_data = {
            'private_key': self.private_key,
            'public_key': self.public_key,
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
            'Crypto-Pay-API-Token': self.private_key
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
    
    async def balance(self, rates, all_currencies=False):
        self.rates = rates
        if self.payment_system == 'payid19':
            answer, answer2 = await self.balance_payid19()
            if answer and isinstance(answer2, Union[int, float]):
                if all_currencies:
                    balances = {"overall": answer + answer2,"usdt": answer, "usdt_blocked": answer2}
                    return from_dict(BalancePayid19, balances)
                else:
                    return answer + answer2
            else:
                return 0
        elif self.payment_system == 'crypto_bot':
            answer = await self.balance_crypto_bot()
            if all_currencies:
                currencies = ['USDT', 'BTC']
                balances = {}
                for balance in answer:
                    if balance['currency_code'] in currencies:
                        if balance['currency_code'] == 'USDT':
                            balance['available'] = round(float(balance['available']), 2)
                        balances[balance['currency_code'].lower()] = float(balance['available'])
                balances['overall'] = sum(map(self.exchange_to_usd, answer[:3]))
                return from_dict(BalanceCryptobot, balances)
            else:
                if not answer: return 0
                return sum(map(self.exchange_to_usd, answer[:3]))
        elif self.payment_system == 'crystal_pay':
            answer_bad = await self.balance_crystal_pay()
            if not answer_bad: return 0
            answer = answer_bad.copy()
            for ans in answer_bad:
                if ans not in ['BITCOIN', 'BTCCRYPTOBOT', 'USDTCRYPTOBOT', 'TRON', 'USDTTRC', 'LZTMARKET']:
                    answer.pop(ans)
            if all_currencies:
                rewrite_dict = {
                    'LZTMARKET': 'rub', 'BTCCRYPTOBOT': 'btc_crypto', 'BITCOIN': 'btc', 'TRON': 'trx', 'USDTCRYPTOBOT': 'usdt_crypto', 'USDTTRC': 'usdt'}
                balances = {}
                for balance in answer:
                    if balance in rewrite_dict:
                        if rewrite_dict[balance] in ['trx', 'usdt', 'usdt_crypto']:
                            answer[balance]['amount'] = round(answer[balance]['amount'], 2)
                        balances[rewrite_dict[balance]] = answer[balance]['amount']
                all_balances = [{'currency_code': answer[balance]['currency'],
                            'available': answer[balance]['amount']} if answer[balance]['currency'] not in ['RUB', 'TRX'] else {'currency_code': 'USDT',
                                                                                                                                'available': await Utils().to_usdt(answer[balance]['currency'], rates, answer[balance]['amount'])} for balance in answer]
                balances['overall'] = sum(map(self.exchange_to_usd, all_balances))
                return from_dict(BalanceCrystalpay, balances)
            else:
                balances = [{'currency_code': answer[balance]['currency'],
                            'available': answer[balance]['amount']} if answer[balance]['currency'] not in ['RUB', 'TRX'] else {'currency_code': 'USDT',
                                                                                                                                'available': await Utils().to_usdt(answer[balance]['currency'], rates, answer[balance]['amount'])} for balance in answer]
                return sum(map(self.exchange_to_usd, balances))
    
    async def max_balance(self, currency):
        if self.payment_system == 'payid19':
            answer, answer2 = await self.balance_payid19()
            return answer
        elif self.payment_system == 'crystal_pay':
            answer = await self.balance_crystal_pay()
            rewrite_dict = {
                'LZTMARKET': 'rub', 'BTCCRYPTOBOT': 'btc_crypto', 'BITCOIN': 'btc', 'TRON': 'trx', 'USDTCRYPTOBOT': 'usdt_crypto', 'USDTTRC': 'usdt'}
            for balance in answer:
                if rewrite_dict[balance] == currency:
                    return answer[balance]['amount']
        elif self.payment_system == 'crypto_bot':
            answer = await self.balance_crypto_bot()
            for balance in answer:
                if balance['currency_code'] == currency.upper():
                    return balance['available']
        else:
            return None
    
    async def balance_payid19(self):
        request_data = {
            'private_key': self.private_key,
            'public_key': self.public_key
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://payid19.com/api/v1/get_balance', data=request_data)
        data = await response.json()
        async with session as close_session:
            pass
        if data['status'] == 'success':
            return float(data['balance']), float(data['blocked_balance'])
        else:
            return None, None
    
    async def get_trx_crystal_pay(self):
        body = {
            'auth_login': 'pos1er',
            'auth_secret': self.public_key,
            'tickers': ['TRX']
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://api.crystalpay.io/v2/ticker/get/', json=body)
        data = await response.json(content_type="text/html")
        async with session as close_session: pass
        if not data['error']:
            return data['currencies']['TRX']['price']
    
    async def balance_crypto_bot(self):
        headers = {
            'Crypto-Pay-API-Token': self.private_key
        }
        session = aiohttp.ClientSession(headers=headers)
        response = await session.get('https://pay.crypt.bot/api/getBalance')
        data = await response.json()
        async with session as close_session: pass
        if 'result' in data:
            return data['result']
    
    async def balance_crystal_pay(self):
        body = {
            'auth_login': 'pos1er',
            'auth_secret': self.public_key,
            'hide_empty': False
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://api.crystalpay.io/v2/balance/info/', json=body)
        try:
            data = await response.json(content_type="text/html")
        except:
            return 0
        async with session as close_session: pass
        if not data['error']:
            return data['balances']
    
    async def exchange_rates(self):
        headers = {
            'Crypto-Pay-API-Token': self.private_key
        }
        session = aiohttp.ClientSession(headers=headers)
        response = await session.get('https://pay.crypt.bot/api/getExchangeRates')
        data = await response.json()
        async with session as close_session: pass
        return data['result']

    def exchange_to_usd(self, data):
        for rate in self.rates:
            if rate['source'] == data['currency_code'] and rate['target'] == 'USD':
                return round(float(data['available']) * float(rate['rate']), 2)
    
    async def withdraw(self, currency, amount, wallet):
        withdraw_id = await get_id_database('withdraws')
        request_id = withdraw_id
        if self.payment_system == 'payid19':
            answer = await self.withdraw_payid19(wallet, currency, round(amount))
        elif self.payment_system == 'crystal_pay':
            if currency == 'rub':
                amount = round(amount)
            request_id = await self.withdraw_crystal_pay(withdraw_id, wallet, currency, amount)
            if request_id:
                answer = True
            else:
                answer = False
        elif self.payment_system == 'crypto_bot':
            answer = await self.withdraw_crypto_bot(withdraw_id, wallet, currency, amount)
        else:
            return None
        new_withdraw = {
                'id': withdraw_id,
                'request_id': request_id,
                'user_id': self.user_id,
                'payment_system': self.payment_system,
                'amount': amount,
                'wallet': wallet,
                'currency': currency,
                'status': answer,
                'timestamp': datetime.datetime.utcnow().timestamp()
            }
        withdraws_db.insert_one(new_withdraw)
        if answer:
            result = {
                'num': withdraw_id,
                'tronscan': None
            }
            return result
    
    async def withdraw_payid19(self, wallet, currency, amount):
        request_data = {
            'private_key': self.private_key,
            'public_key': self.public_key,
            'address': wallet,
            'amount': amount,
            'coin': currency.upper()
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://payid19.com/api/v1/create_withdraw', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if data:
            if data['status'] == 'success':
                return True
    
    async def withdraw_crypto_bot(self, withdraw_id, wallet, currency, amount):
        headers = {
            'Crypto-Pay-API-Token': self.private_key
        }
        request_data = {
            'user_id': wallet,
            'asset': currency.upper(),
            'amount': amount,
            'spend_id': withdraw_id
        }
        session = aiohttp.ClientSession(headers=headers)
        response = await session.post('https://pay.crypt.bot/api/transfer', data=request_data)
        data = await response.json()
        async with session as close_session: pass
        if 'result' in data:
            return True

    async def withdraw_crystal_pay(self, withdraw_id, wallet, currency, amount):
        rewrite_dict = {
            'rub': 'LZTMARKET', 'btc_crypto': 'BTCCRYPTOBOT', 'btc': 'BITCOIN', 'trx': 'TRON', 'usdt_crypto': 'USDTCRYPTOBOT', 'usdt': 'USDTTRC'}
        body = {
            'auth_login': 'pos1er',
            'auth_secret': self.public_key,
            'signature': hashlib.sha1(f'{amount}:{rewrite_dict[currency]}:{wallet}:{self.private_key}'.encode('utf-8')).hexdigest(),
            'amount': amount,
            'method': rewrite_dict[currency],
            'wallet': wallet,
            'subtract_from': 'amount',
            'extra': f'{withdraw_id}'
        }
        session = aiohttp.ClientSession()
        response = await session.post('https://api.crystalpay.io/v2/payoff/create/', json=body)
        data = await response.json(content_type="text/html")
        async with session as close_session: pass
        if not data['error']:
            request_id = data['id']
            body = {
                'auth_login': 'pos1er',
                'auth_secret': self.public_key,
                'signature': hashlib.sha1(f'{request_id}:{self.private_key}'.encode('utf-8')).hexdigest(),
                'id': f'{request_id}'
            }
            session = aiohttp.ClientSession()
            response = await session.post('https://api.crystalpay.io/v2/payoff/submit/', json=body)
            data = await response.json(content_type="text/html")
            async with session as close_session: pass
            if not data['error']:
                return request_id