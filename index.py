import threading
from threading import Thread
from datetime import datetime
import asyncio, os, time
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import LinkPreviewOptions
# from config_reader import config
from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

from handlers import questions, add_kata, different_types

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(TOKEN)
dp = Dispatcher()

from push.msg import send_push_notification, push_msg
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # For StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

async def async_wrapper():
    await push_msg(bot, chat_id)

async def main():
    print('Start...')
    dp.include_router(add_kata.router)
    dp.include_router(questions.router)
    dp.include_router(different_types.router)

    loop = asyncio.get_running_loop()

#     ToDo time custom
    scheduler = AsyncIOScheduler(event_loop=loop)
    scheduler.add_job(async_wrapper,
                        'cron',
                        hour=9,
                        minute=5,
                        misfire_grace_time=40)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем бота

    print("Бот запущен!")
    asyncio.run(main())




