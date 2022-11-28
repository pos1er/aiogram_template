import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from data.config import TOKEN

bot = Bot(token=TOKEN, parse_mode='HTML')
storage = MemoryStorage()
loop = asyncio.get_event_loop()
dp = Dispatcher(storage=storage, loop=loop)

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
