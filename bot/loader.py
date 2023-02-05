from time import timezone
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage
from bot.data.config import MAIN_TOKEN, REDIS_URL
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

bot = Bot(token=MAIN_TOKEN, parse_mode='HTML')
storage = RedisStorage.from_url(REDIS_URL)
jobstores = {
    'default': RedisJobStore(jobs_key='dispatcher_trips_jobs',
                             run_times_key='dispatcher_trips_running',
                             host='localhost',
                             db=2,
                             port=6379)
}
scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=jobstores))
scheduler.ctx.add_instance(bot, declared_class=Bot)
#  storage = MemoryStorage()
# loop = asyncio.get_event_loop()
dp = Dispatcher(storage=storage)
