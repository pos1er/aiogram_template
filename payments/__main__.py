from json import JSONDecodeError
from aiogram import html
from bot.data.config import DEFAULT_LANGUAGE
from fastapi import HTTPException, Request
from aiogram.utils.i18n import I18n
import uvicorn
from bot.handlers.admins.any_admin import notification
from bot.keyboards.inline.user import profile_keyboard
from bot.utils.workdir import WORKDIR

from payments.loader import app
from bot.loader import bot
from bot.utils.loggers import payment_logger
from bot.mongodb.mongodb import MainEdits, MainGets, Payments, Users, Utils


@app.post('/qshop-pay')
async def check_pay(req: Request):
    i18n = I18n(path=WORKDIR / "locales",
                default_locale=DEFAULT_LANGUAGE, domain='messages')
    _ = i18n.gettext
    try:
        update_data = await req.json()
    except JSONDecodeError:
        update_data = await req.form()
    if 'payload' in update_data:
        purchase_way = 'crypto_bot'
        payment_system_name = '⚡️ CryptoBot'
        invoice_data = update_data['payload']
        payment_id = invoice_data['invoice_id']
        check_data = invoice_data['hash']
    elif 'createdDateTime' in update_data:
        purchase_way = 'qiwi'
        payment_system_name = '⚖️ Qiwi/Карта'
        payment_id = int(update_data['id'])
        check_data = update_data['status']
    else:
        purchase_way = 'payid19'
        payment_system_name = '🦅 PayID19'
        payment_id = int(update_data['order_id'])
        check_data = update_data['privatekey']
    check_web = await Payments(purchase_way, dont_check_id=True).check_webhook(check_data)
    if not check_web:
        payment_logger.info('Неверный запрос')
        raise HTTPException(200, "ok")
    check_closed = await MainGets().check_payment(payment_id)
    if not check_closed:
        payment_logger.info('Уже закрытый платеж или время вышло')
        raise HTTPException(200, "ok")
    payment_logger.info('Получена оплата')
    additional_data = {'ip': None, 'email': None}
    money, currency_code, currency_symbol, user_id, message_id, pay_id = await MainGets().close_payment(payment_id)
    user_language = await MainGets().get_language(user_id)
    user_currency_symbol, user_currency_code = await MainGets().user_currency_symbol(user_id, code=True)
    if user_currency_code != currency_code:
        currency_symbol = user_currency_symbol
        money = await Utils().int_to_asset(money, currency_code, user_currency_code)
        currency_code = user_currency_code
    if purchase_way == 'payid19':
        additional_data = await Users(user_id).add_additional_data(update_data['ip'], update_data['email'], payment_id)
    money_with_promo = None
    promo_text = ''
    promo_id = await MainGets().get_sale(user_id)
    if promo_id:
        promo_data = await MainGets().get_promo_code(promo_id, user_language)
        if promo_data:
            if promo_data.type == 'payment_bonus':
                await Users(user_id).reset_sale()
                money_get = Utils().round_down(
                    money * promo_data.sale / 100, 2)
                promo_text = _('\n\n🎁 Был применен промокод <code>{promo_code}</code> <b>(+{money_get}{currency_symbol})</b>', locale=user_language).format(
                    money_get=f'{money_get:g}', promo_code=promo_data.code, currency_symbol=currency_symbol)
                additional_data['promo_code'] = f'<code>{promo_data.code}</code> <b>(+{money_get}{currency_symbol})</b>'
                money_with_promo = Utils().round_down(money + money_get, 2)
                await MainEdits().add_to_promo_code(payment_id, promo_id, money_get)
        else:
            await Users().reset_sale_force()
    if money_with_promo:
        text = _('<b>⚡️ Успешное пополнение баланса на сумму</b> <code>{money_with_promo}{currency_symbol}</code>{promo_text}', locale=user_language).format(
            money_with_promo=f'{money_with_promo:g}', currency_symbol=currency_symbol, promo_text=promo_text)
        await MainEdits().add_money(money_with_promo, user_id, currency_code)
    else:
        additional_data['promo_code'] = None
        text = _('<b>⚡️ Успешное пополнение баланса на сумму</b> <code>{money}{currency_symbol}</code>', locale=user_language).format(
            money=f'{money:g}', currency_symbol=currency_symbol)
        await MainEdits().add_money(money, user_id, currency_code)
    await bot.delete_message(message_id=message_id, chat_id=user_id)
    await bot.send_sticker(chat_id=user_id, sticker='CAACAgIAAxkBAAEIIspkEJZmErw2s5fOwwzhe0kqu93dQwACZC0AAgspiUjfvHrUinnkzS8E')
    await bot.send_message(chat_id=user_id, text=text, reply_markup=profile_keyboard(_, user_language))
    referral, language = await MainGets().get_referral(user_id)
    user_full_name = await Utils().get_full_name(user_id)
    if referral:
        ref_symbol, ref_code = await MainGets().user_currency_symbol(referral, code=True)
        money_currency = await Utils().int_to_asset(money, currency_code, ref_code)
        ref_amount = Utils().round_down(money_currency * 0.05, 2)
        text_referral = _(
            '<b>⚡️ Поздравляем!</b>\n👥 Ваш реферал пополнил баланс на <code>{money_currency}{ref_symbol}</code>\n\n<b>⭐️ Пользователь</b> — {user}\n<b>💸 Вы получаете выплату</b> — <code>{ref_amount}{ref_symbol}</code>', locale=language).format(
                money_currency=f'{money_currency:g}', ref_symbol=ref_symbol, ref_amount=f'{ref_amount:g}', user=html.link(html.quote(user_full_name),
                                                                                                                f"tg://user?id={user_id}") + f" [{user_id}]"
            )
        await bot.send_message(chat_id=referral, text=text_referral)
        await MainEdits().add_money(ref_amount, referral, ref_code)
        await MainEdits().add_to_referal(payment_id, referral)
        ref_full_name = await Utils().get_full_name(referral)
        additional_data['referral'] = html.link(html.quote(
            ref_full_name), f"tg://user?id={referral}") + f" [{referral}]" + f" <code>+{Utils().round_down(money * 0.05, 2)}{currency_symbol}</code>"
    else:
        additional_data['referral'] = None
    amount = money_with_promo if money_with_promo else money
    await notification('payment', {'payment_id': pay_id,
                                   'user': html.link(html.quote(user_full_name),
                                                     f"tg://user?id={user_id}") + f" [{user_id}]",
                                   'amount': Utils().normalize(amount),
                                   'currency': currency_symbol, 'currency_code': currency_code,
                                   'payment_system': payment_system_name}, 'payments', user_id=user_id,
                       additional_data=additional_data)
    raise HTTPException(200, "ok")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7773)
