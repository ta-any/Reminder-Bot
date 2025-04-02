from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



# from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
# from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardRemove

def get_yes_or_no() -> ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Yes", callback_data="has_account_yes"),
        InlineKeyboardButton(text="No", callback_data="has_account_no")
    )

    return builder.as_markup()

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


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