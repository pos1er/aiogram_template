from time import timezone
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage
from bot.data.config import MAIN_TOKEN, REDIS_URL
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = Bot(token=MAIN_TOKEN, parse_mode='HTML')
storage = RedisStorage.from_url(REDIS_URL)
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
#  storage = MemoryStorage()
# loop = asyncio.get_event_loop()
dp = Dispatcher(storage=storage)
