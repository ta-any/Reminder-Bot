from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.for_questions import get_yes_or_no, create_keyboard_btn, make_row_keyboard
from aiogram.types import LinkPreviewOptions
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # For StatesGroup

from server.repo import add_kata_on_name, c_in_c

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
    language = State()

tmp = {}

@router.message(Form.username)
async def get_name(message: Message, state: FSMContext):
    name = message.text
    if len(name) < 3:
       await message.answer("Username слишком короткий. Попробуйте еще раз:")
       return

    print("FROM GET_NAME: ", name)
    result = await c_in_c(name)
    if result:
        await message.answer(f"Ваш username Codewars: {name}")
        list_langs = create_keyboard_btn(result)

        # Сохраняем имя пользователя Codewars в состояние
        await state.update_data(codewars_username=name)

        await message.answer(
            text="Выберите язык:",
            reply_markup=make_row_keyboard(list_langs)
        )
        await state.set_state(Form.language)  # Устанавливаем состояние выбора языка
    else:
        await message.answer("Username не существует. Попробуйте еще раз или давайте создадим аккаунт")
        return

    # Don't clear state here if you're transitioning to language selection
    # await state.clear()


@router.message(Form.language)
async def process_language(message: Message, state: FSMContext):
    # Получаем выбранный язык
    selected_language = message.text

    # Здесь можно добавить логику обработки выбранного языка
    print(f"User selected language: {selected_language}")

    await message.answer(
        text=f"Вы выбрали язык: {selected_language}",
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру
    )

    await state.clear()


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






