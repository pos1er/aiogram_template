
from dataclasses import dataclass


@dataclass
class BalanceData:
    overall: float
    payid19: float
    crypto_bot: float
    crystal_pay: float


@dataclass
class BalancePayid19:
    overall: float
    usdt: float
    usdt_blocked: float


@dataclass
class BalanceCryptobot:
    overall: float
    btc: float
    usdt: float


@dataclass
class BalanceCrystalpay:
    overall: float
    btc: float
    usdt: float
    rub: float
    btc_crypto: float
    usdt_crypto: float
    trx: float