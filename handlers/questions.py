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

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer( "Welcome!" )
    await asyncio.sleep(1.3)
    await message.answer(
        "Есть ли аккаунт Codewars?",
        reply_markup=get_yes_or_no()
    )

class Form(StatesGroup):
    username = State()

@router.message(Form.username)
async def get_name(message: Message, state: FSMContext):
    name = message.text.lower()
    await message.answer(f"Ваш username Codewars: {name}")

    await state.finish()


@router.callback_query(F.data == "has_account_yes")
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Отлично! Введите ваш username Codewars!")
    await state.set_state(Form.username)

    await callback.answer()

@router.callback_query(F.data == "has_account_no")
async def send_random_value(callback: types.CallbackQuery):
    links_text = (
        "https://www.codewars.com/"
    )
    option_link = LinkPreviewOptions(
        url="https://www.codewars.com/",
        prefer_small_media=True
    )
    await callback.message.answer(
        f"Регистрация \n{links_text}",
        link_preview_options=option_link
    )
    await callback.answer()

#
# @router.message(F.text.lower() == "has_account_yes")
# async def answer_yes(message: Message):
#     await message.answer(
#         "Это здорово!",
#         reply_markup=ReplyKeyboardRemove()
#     )
#
# @router.message(F.text.lower() == "has_account_no")
# async def answer_no(message: Message):
#     await message.answer(
#         "Жаль...",
#         reply_markup=ReplyKeyboardRemove()
#     )



