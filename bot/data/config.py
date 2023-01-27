import os

from dotenv import load_dotenv

load_dotenv()

mongodb_url = str(os.getenv("MONGODB_LINK"))

MAIN_TOKEN = str(os.getenv("MAIN_TOKEN"))

BASE_URL = str(os.getenv("BASE_URL"))

CAPTCHA_DURATION = int(os.getenv("CAPTCHA_DURATION"))

REDIS_URL = str(os.getenv("REDIS_URL"))

crystal_pay_key = str(os.getenv("CRYSTAL_PAY_KEY"))

public_key_payid19 = str(os.getenv("PUBLIC_KEY_PAYID19"))

private_key_payid19 = str(os.getenv("PRIVATE_KEY_PAYID19"))

crypto_bot_key = str(os.getenv("CRYPTO_BOT_KEY"))
