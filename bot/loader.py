from aiogram import Bot, Dispatcher
from bot.data.config import MAIN_TOKEN, REDIS_URL, TESTING_BOT
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

bot = Bot(token=MAIN_TOKEN, parse_mode='HTML')

if TESTING_BOT:
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()

else:
    from aiogram.fsm.storage.redis import RedisStorage
    storage = RedisStorage.from_url(REDIS_URL)
    jobstores = {
        'default': RedisJobStore(jobs_key='dispatcher_trips_jobs',
                                run_times_key='dispatcher_trips_running',
                                host='localhost',
                                db=2,
                                port=6379)
    }
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)

dp = Dispatcher(storage=storage)
