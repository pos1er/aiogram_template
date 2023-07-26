import os

from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = str(os.getenv("MONGODB_LINK"))

MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID"))

MAIN_TOKEN = str(os.getenv("MAIN_TOKEN"))

BASE_URL = str(os.getenv("BASE_URL"))

CAPTCHA_DURATION = int(os.getenv("CAPTCHA_DURATION"))

REDIS_URL = str(os.getenv("REDIS_URL"))

CRYSTAL_PAY_KEY = str(os.getenv("CRYSTAL_PAY_KEY"))

PUBLIC_KEY_PAYID19 = str(os.getenv("PUBLIC_KEY_PAYID19"))

PRIVATE_KEY_PAYID19 = str(os.getenv("PRIVATE_KEY_PAYID19"))

CRYPTO_BOT_KEY = str(os.getenv("CRYPTO_BOT_KEY"))

WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT"))

BOT_PATH = str(os.getenv("BOT_PATH"))

TESTING_BOT = int(os.getenv("TESTING_BOT"))

DEFAULT_LANGUAGE = str(os.getenv("DEFAULT_LANGUAGE"))
