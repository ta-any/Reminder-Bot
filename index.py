import telebot, os, schedule, time, sys, asyncio, requests
from dotenv import load_dotenv
from telebot import formatting, types
from contextlib import contextmanager
from server.basedate.bd import random_kata, append_kata, change_status

load_dotenv()
TOKEN = os.getenv("API_KEY_BOT")  # Имя должно совпадать с .env
chat_id = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

# То что запишим в кэш (Redis)
user_data = {}

def check_in_codewars(user_id, user):
        url = f"https://www.codewars.com/api/v1/users/{user}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.ok:
                print("Успешный запрос!")
                user_data[user_id]['body'] = response.json()
                print("-------------------------------------")
                print(user_data[user_id]['body'])
                print("-------------------------------------")
                return True
            else:
                print(f"Ошибка запроса. Статус код: {response.status_code}")
                return False

        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return []

def create_keyboard_btn(user_data):
    lst = list(user_data['ranks']['languages'])

    if lst:
        print("Список не пустой")
        lst.append("Скрыть меню")
    else:
        print("Список пустой")
        lst.extend(['python', 'javascript', 'rust', 'typescript', "Скрыть меню"])

    return lst


def open_menu(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
#         persistent=True,  # Не скрывается после использования
#         selective=True    # В группах показывается только выбранным пользователям
    )
    markup.add("/start", "Добавить Задачу")
    markup.add("Скрыть меню")

    bot.send_message(
        message.chat.id,
        "Что хотите сделать?",
        reply_markup=markup
    )


@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    print("Info about chat: ", chat_id, user_id)
    bot.send_message(chat_id, 'Добро пожаловать!')

    time.sleep(1.5)
    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Да, есть аккаунт", callback_data="has_account")
    btn_no = types.InlineKeyboardButton("Нет, создать", callback_data="no_account")
    markup.add(btn_yes, btn_no)

    bot.send_message(chat_id, 'Есть ли аккаунт Codewars?', reply_markup=markup)

    user_data[user_id] = {"state": "waiting_account_info"}
    print('user_data', user_data)


    @bot.callback_query_handler(func=lambda call: call.data in ["has_account", "no_account"])
    def handle_account_choice(call):
        if call.data == "has_account":
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
            msg = bot.send_message(chat_id, 'Отлично! Введите ваш username Codewars:')
            print("USERNAME: ", msg)

            bot.register_next_step_handler(msg, process_username)

        else:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
            bot.send_message(chat_id, 'Давайте создадим аккаунт: https://www.codewars.com/')

            user_data[user_id] = {"state": "no_account"}


def process_username(message):
    user_id = message.from_user.id
    username = message.text.strip()

    # Простая валидация
    if len(username) < 3:
        msg = bot.send_message(message.chat.id, "Username слишком короткий. Попробуйте еще раз:")
        bot.register_next_step_handler(msg, process_username)
        return

    if check_in_codewars(user_id, username):
        # Сохраняем username
        user_data[user_id]["user_name"] = username
        user_data[user_id]["state"] = "username_received"

        # Подтверждение
        bot.send_message(message.chat.id, f"Спасибо, {username}! Ваши данные сохранены.")
        chose_lang(message)
    else:
        msg = bot.send_message(message.chat.id, "Username не существует. Попробуйте еще раз или давайте создадим аккаунт")
        bot.register_next_step_handler(msg, process_username)
        return

def chose_lang(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
#         persistent=True,  # Не скрывается после использования
#         selective=True    # В группах показывается только выбранным пользователям
    )
    lst = create_keyboard_btn(user_data[user_id]["body"])
    user_data[user_id]["languages"] = lst

    for btn in lst:
        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Выберите язык для задач",
        reply_markup=markup
    )


@bot.message_handler(commands=['menu'])
def menu_command(message):
    print('menu')

# TODO - languages
# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
     msg = bot.send_message(message.chat.id,  message.text)
     print('languages: ', msg)
#     bot.reply_to(message, message.text)


@bot.message_handler(commands=['menu'])
def menu_command(message):
    print('menu')
    open_menu(message)


@bot.message_handler(func=lambda message: message.text == 'Скрыть меню')
def remove_keyboard(message):
    chat_id = message.chat.id
    print('Here close menu')
    bot.edit_message_reply_markup(chat_id, reply_markup=None)

@bot.message_handler(func=lambda message: message.text == 'Code')
def send_safe_code(message):
    print("STart code: ")
    raw_code = """
        Пример кода на Python:

        def hello_world():
            print("Hello, World!")

        hello_world()
    """
    safe_code = formatting.escape_markdown(raw_code)
    bot.send_message(message.chat.id, f"```\n{safe_code}\n```",
                   parse_mode='MarkdownV2')
    bot.send_message(message.chat.id, reply_markup=None)

def get_lst_msg(data):
    name_task = data[1]
    link_task = data[3]

    return [f'Good morning! Готовы решить задачу?', f'{link_task}', f'{name_task}\n Задача и ее описание полученное из апи']

def send_notification(chat_id, data):
    try:
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("Сделаю это", callback_data="task_yes")
        btn_no = types.InlineKeyboardButton("Нет, выбрать другую", callback_data="task_no")
        markup.add(btn_yes, btn_no)
        message = get_lst_msg(data)
        bot.send_message(chat_id, F'{message[0]} {message[1]}')

        time.sleep(1.5)
        bot.send_message(chat_id, message[2], reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: call.data in ["task_yes", "task_no"])
        def handle_account_choice(call):
            if call.data == "task_yes":
                bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                msg = bot.send_message(chat_id, 'Отлично! Ждем результатов!')
                user_data['today_task'] = None
                user_data['today_task'] = data
                print("DATA from push:", user_data)
                # Обратимся в АПИ чтобы сменить статус задачи на в процессе
                change_status(data[0], 2)

            else:
                bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                txt = random_kata()  # Получаем данные (предполагается, что это список/кортеж)
                msg = get_lst_msg(txt)

                message = f'Хорошо! Давайте попробуем эту {msg[1]}'
                bot.send_message(chat_id, message)
                bot.send_message(chat_id, f'{msg[2]}')
                # Пока так же тыкаемся в апи и сохраняем задачу в статусе ожидание
                # Если не подойдет эта, нужно думать над логикой дальше


    except telebot.apihelper.ApiTelegramException as e:  # Лучше ловить конкретное исключение
        print(f"Ошибка отправки: {e}")

def daily_notification(chat_id):
    txt = random_kata()  # Получаем данные (предполагается, что это список/кортеж)

    if not txt or len(txt) < 4:
        print("Ошибка: некорректные данные из random_kata()")
        return

    print(txt)

    send_notification(chat_id, txt)  # Замените chat_id на реальный


daily_notification(chat_id)

# Запускаем бота
print("Бот запущен!")

bot.polling()