from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_yes_or_no() -> ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Yes", callback_data="has_account_yes"),
        InlineKeyboardButton(text="No", callback_data="has_account_no")
    )

    return builder.as_markup()

def isDone() -> ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Сделаю!", callback_data="process"),
        InlineKeyboardButton(text="Хочу другую!", callback_data="other_kata")
    )

    return builder.as_markup()

def make_row_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект inline-клавиатуры
    """
    row = [InlineKeyboardButton(text=item, callback_data=f"confirm_{item}") for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[row])

def make_row_keyboard_level(items: list[str]) -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект inline-клавиатуры
    """
    row = [InlineKeyboardButton(text=item, callback_data=f"level_{item}") for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[row])


def create_keyboard_btn(user_data):
    lst = list(user_data['ranks']['languages'])

    if lst:
        print("Список не пустой")
        lst.append("Скрыть меню")
    else:
        print("Список пустой")
        lst.extend(['python', 'javascript', 'rust', 'typescript', "Скрыть меню"])

    return lst

# def get_yes_no_kb() -> ReplyKeyboardMarkup:
#     kb = ReplyKeyboardBuilder()
#     kb.button(text="Да")
#     kb.button(text="Нет")
#     kb.adjust(2)
#     return kb.as_markup(resize_keyboard=True)