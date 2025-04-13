import asyncio, time
from datetime import datetime
from server.repo import random_kata_by_day, get_info_kata_body
from aiogram.types import LinkPreviewOptions

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # For StatesGroup

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.for_questions import isDone

from handlers import random_kata

dp = Dispatcher()
router = Router()

async def send_push_notification(bot, chat_id):
    res = await random_kata_by_day()
    link = res['url']
    links_text = (f'{link}')
    option_link = LinkPreviewOptions(
        url=f'{link}',
        prefer_small_media=True
    )
    name_kata = res['title'] or "Задача без названия"
    data = await get_info_kata_body(name_kata)
    body_kata = res['description'] or "Описание задачи отсутствует"

    await bot.send_message(chat_id=chat_id, text=f"Доброе утро! {name_kata} Ваша задача на сегодня!", link_preview_options=option_link)
    await asyncio.sleep(1)



async def push_msg(bot, chat_id: int):
    await send_push_notification(bot, chat_id)







