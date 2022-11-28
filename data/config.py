import os

from dotenv import load_dotenv

load_dotenv()

mongodb_url = str(os.getenv("MONGODB_LINK"))

TOKEN = str(os.getenv("TOKEN"))

crystal_pay_key = str(os.getenv("CRYSTAL_PAY_KEY"))

public_key_payid19 = str(os.getenv("PUBLIC_KEY_PAYID19"))

private_key_payid19 = str(os.getenv("PRIVATE_KEY_PAYID19"))

crypto_bot_key = str(os.getenv("CRYPTO_BOT_KEY"))
