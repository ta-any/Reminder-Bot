from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.for_questions import get_yes_or_no
from aiogram.types import LinkPreviewOptions
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # For StatesGroup
from server.repo import add_kata_on_name

router = Router()
class Kata(StatesGroup):
    name = State()

@router.message(Command("add_kata"))
async def cmd_add_kata(message: Message, state: FSMContext):
    await message.answer( "Сообщите название задачи или пришлите ссылку" )
    await state.set_state(Kata.name)



@router.message(Kata.name)
async def get_name(message: Message, state: FSMContext):
    name = message.text
    print('-----------------------Kata.namekata--------------------------------------')
    print("NAME: ", name)
    result = await add_kata_on_name(name, 'python')

    if(result):
        await message.answer(f"Ваша задача добавленна!")
    else:
        await message.answer(f"Такой задачи не существует, попробуйте еще раз!")
        return

    await state.clear()






