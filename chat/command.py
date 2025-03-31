from telebot import formatting, types
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
import asyncio

from server.basedate.bd import random_kata, append_kata, change_status
from server.repo import add_kata_on_name


# TOKEN = os.getenv("API_KEY_BOT")
# bot = AsyncTeleBot(TOKEN)

class BotHandler:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        async def start(message):
            # Создаем inline-кнопки
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("Да, есть аккаунт", callback_data="has_account")
            btn2 = types.InlineKeyboardButton("Нет, создать", callback_data="no_account")
            markup.add(btn1, btn2)

            await self.bot.send_message(
                message.chat.id,
                "Есть ли аккаунт Codewars?",
                reply_markup=markup
            )

            user_data = {}
            user_data[user_id] = {"state": "waiting_account_info"}
            print('user_data', user_data)

        @self.bot.callback_query_handler(func=lambda call: call.data in ["has_account", "no_account"])
        async def callback_handler(call):
            chat_id = call.message.chat.id
            user_id = call.from_user.id

            if call.data == "has_account":
                print("BTH: has_account")
                await self.bot.answer_callback_query(call.id, "has_account!")
                msg = await self.bot.send_message(chat_id, "Отлично! Введите ваш username Codewars:")

                # Регистрируем следующий шаг (передаем метод без вызова и без await)
                self.bot.register_next_step_handler(msg, self.process_username)

            elif call.data == "no_account":
                await self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                await self.bot.send_message(chat_id, 'Давайте создадим аккаунт: https://www.codewars.com/')
                self.user_data[user_id] = {"state": "no_account"}

    async def process_username(self, message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        print('START PROCESS_USERNAME')
        username = message.text.strip()

        # Инициализируем user_data если еще не существует
        if user_id not in self.user_data:
            self.user_data[user_id] = {}

        # Простая валидация
        if len(username) < 3:
            msg = await self.bot.send_message(chat_id, "Username слишком короткий. Попробуйте еще раз:")
            self.bot.register_next_step_handler(msg, self.process_username)
            return

        # Проверяем существование пользователя в Codewars
        if await self.check_in_codewars(user_id, username):  # Предполагается, что этот метод есть в вашем классе
            # Сохраняем username
            self.user_data[user_id]["user_name"] = username
            self.user_data[user_id]["state"] = "username_received"

            # Подтверждение
            await self.bot.send_message(chat_id, f"Спасибо, {username}! Ваши данные сохранены.")
            # await self.chose_lang(message)  # Раскомментируйте, если метод существует
        else:
            msg = await self.bot.send_message(chat_id, "Username не существует. Попробуйте еще раз или давайте создадим аккаунт")
            self.bot.register_next_step_handler(msg, self.process_username)

