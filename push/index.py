# async def scheduled_notification(bot: Bot):
#     while True:
#         await asyncio.sleep(3600)  # Каждый час
#         await bot.send_message(chat_id, "Ежечасное уведомление")

# В main():
# asyncio.create_task(scheduled_notification(bot))
import asyncio, time
from datetime import datetime
from server.repo import random_kata_by_day
from aiogram.types import LinkPreviewOptions

async def send_push_notification(bot, chat_id):
    res = await random_kata_by_day()
    link = res['url']
    links_text = (f'{link}')
    option_link = LinkPreviewOptions(
        url=f'{link}',
        prefer_small_media=True
    )
    body_kata = res['description'] or "Описание задачи отсутствует"  # Запасной вариант
    name_kata = res['title'] or "Задача без названия"  # Запасной вариант

    await bot.send_message(chat_id=chat_id, text=f"Доброе утро! {name_kata} Ваша задача на сегодня!", link_preview_options=option_link)
    await asyncio.sleep(1)
    await bot.send_message(chat_id=chat_id, text=body_kata)
    await bot.send_message(chat_id=chat_id, text="Готовы ее выполнить?")
    #TODO - продлить ветку с логикой!


async def push_msg(bot, chat_id: int):
    while True:
        # Получаем текущее время
        now = datetime.now().timestamp()
        print("NOW: ", now)
        print("====================================")
        await send_push_notification(bot, chat_id)

        time.sleep(36000)






