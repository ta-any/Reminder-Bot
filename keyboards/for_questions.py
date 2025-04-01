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

# def get_yes_no_kb() -> ReplyKeyboardMarkup:
#     kb = ReplyKeyboardBuilder()
#     kb.button(text="Да")
#     kb.button(text="Нет")
#     kb.adjust(2)
#     return kb.as_markup(resize_keyboard=True)