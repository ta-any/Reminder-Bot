# import os, schedule, time, sys, asyncio, redis
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
#
# from server.basedate.bd import random_kata, append_kata, change_status
# from server.repo import add_kata_on_name
#
#
# HOST = os.getenv('REDIS_HOST')
# PORT = os.getenv('REDIS_PORT')
# pool = redis.ConnectionPool(host = HOST, port = PORT, db=0)
# r = redis.Redis(connection_pool=pool)
#
#
# load_dotenv()
# TOKEN = os.getenv("API_KEY_BOT")
# chat_id = os.getenv("CHAT_ID")


#
# async def start():
#     @bot.message_handler(commands=['start'])
#     async def start(message):
#         await bot.send_message(
#                         message.chat.id,
#                         "Доброе утро!")
#         await asyncio.sleep(1)
#         # Создаем inline-кнопки
#         markup = types.InlineKeyboardMarkup()
#         btn1 = types.InlineKeyboardButton("Да, есть аккаунт", callback_data="has_account")
#         btn2 = types.InlineKeyboardButton("Нет, создать", callback_data="no_account")
#         markup.add(btn1, btn2)
#
#         await bot.send_message(
#             message.chat.id,
#             "Есть ли аккаунт Codewars?",
#             reply_markup=markup
#         )
#
#         user_data = {}
#         user_data[user_id] = {"state": "waiting_account_info"}
#         print('user_data', user_data)
#
#     @bot.callback_query_handler(func=lambda call: call.data in ["has_account", "no_account"])
#     async def callback_handler(call):
#         chat_id = call.message.chat.id
#         user_id = call.from_user.id
#         if call.data == "has_account":
#             print("BTH: has_account")
#             await bot.answer_callback_query(call.id, "has_account!!")
#             msg = await bot.send_message(call.message.chat.id, "Отлично! Введите ваш username Codewars!")
#
#             await bot.register_next_step_handler(call.message, process_username)
#
#         elif call.data == "no_account":
#             await bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
#             await bot.send_message(chat_id, 'Давайте создадим аккаунт: https://www.codewars.com/')
#             user_data[user_id] = {"state": "no_account"}
#
#     async def process_username(message):
#         username = message.text
#         await bot.send_message(message.chat.id, f"Ваш username Codewars: {username}")
#
#
#
#
# async def main():
#     await start()
#     print("Бот запущен")
#     await bot.polling()
#
# if __name__ == '__main__':
#     asyncio.run(main())


import asyncio, os
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

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

from handlers import questions, add_kata, different_types

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(TOKEN)
dp = Dispatcher()

from push.index import send_push_notification


# Запуск бота
async def main():
    dp.include_router(add_kata.router)
    dp.include_router(questions.router)

#     dp.include_router(different_types.router)

    await send_push_notification(bot, chat_id)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())