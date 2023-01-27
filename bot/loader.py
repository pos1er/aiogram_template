from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage
from data.config import MAIN_TOKEN, REDIS_URL

bot = Bot(token=MAIN_TOKEN, parse_mode='HTML')
storage = RedisStorage.from_url(REDIS_URL)
#  storage = MemoryStorage()
# loop = asyncio.get_event_loop()
dp = Dispatcher(storage=storage)
