from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram import Bot, Dispatcher, types

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.for_questions import get_yes_or_no, make_row_keyboard_level, create_keyboard_btn, make_row_keyboard
from aiogram.types import LinkPreviewOptions
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # For StatesGroup

from server.repo import add_kata_on_name, c_in_c, parser_data

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    print('Start')
    await message.answer( "Welcome!" )
    await asyncio.sleep(1.3)
    await message.answer(
        "Есть ли аккаунт Codewars?",
        reply_markup=get_yes_or_no()
    )

class Form(StatesGroup):
    username = State()
    language = State()

tmp_config_filter = {}


@router.message(Form.username)
async def get_name(message: Message, state: FSMContext):
    name = message.text
    if len(name) < 3:
       await message.answer("Username слишком короткий. Попробуйте еще раз:")
       return

    print("FROM GET_NAME: ", name)
    result = await c_in_c(name)
    print("========================result=================================")
    print(result)
    if result:
        await message.answer(f"Ваш username Codewars: {name}")
        list_langs = create_keyboard_btn(result)
        print(list_langs)

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


@router.callback_query(lambda c: c.data.startswith('confirm_') or c.data == 'confirm_Скрыть меню')
async def handle_inline_button(callback_query: types.CallbackQuery):
    # Получаем callback_data
    callback_data = callback_query.data

    if callback_data == 'confirm_Скрыть меню':
        await callback_query.message.edit_text("Скрыть меню")
        await callback_query.answer()
        return

    selected_language = callback_data.split('_')[1]

    button_text = next(
        (btn.text for row in callback_query.message.reply_markup.inline_keyboard
         for btn in row if btn.callback_data == callback_data),
        None
    )

    tmp_config_filter['language'] = selected_language
    await callback_query.message.edit_text(
        f"Подтверждено: {selected_language})"
    )
    list_nums = ["1", "2", "3", "4", "5", "6", "7", "8"]

    await callback_query.message.answer(
        text="Выбирать уровень: ",
        reply_markup=make_row_keyboard_level(list_nums)
    )

    await callback_query.answer()
#     await state.clear()



@router.callback_query(lambda c: c.data.startswith('level_'))
async def handle_inline_button(callback_query: types.CallbackQuery):
    # Получаем callback_data
    callback_data = callback_query.data

    selected_level = callback_data.split('_')[1]

    button_text = next(
        (btn.text for row in callback_query.message.reply_markup.inline_keyboard
         for btn in row if btn.callback_data == callback_data),
        None
    )

    tmp_config_filter['level'] = int(selected_level)
    await callback_query.message.edit_text(
        f"Подтверждено: {selected_level}"
    )
    await callback_query.message.answer( text="Это может занять время" )
    await get_base(tmp_config_filter['language'], tmp_config_filter['level'], 100)

    await callback_query.message.answer(
        text="Успешно!"
    )

    await callback_query.answer()
#     await state.clear()

async def get_base(language, kyu, count):
    await parser_data(language, kyu, count)


