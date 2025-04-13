from datetime import datetime
import asyncio, os, time, logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

from handlers import questions, add_kata, different_types, random_kata
from push.msg import send_push_notification, push_msg

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher()


async def async_wrapper():
    await push_msg(bot, chat_id)

async def main():
    print('Start...')
    dp.include_router(add_kata.router)
    dp.include_router(questions.router)
    dp.include_router(random_kata.router)
    dp.include_router(different_types.router)

    loop = asyncio.get_running_loop()

#     ToDo time custom
    scheduler = AsyncIOScheduler(event_loop=loop)
    scheduler.add_job(async_wrapper,
                        'cron',
                        hour=19,
                        minute=57,
                        misfire_grace_time=40)

    scheduler.start()

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен!")
    asyncio.run(main())




