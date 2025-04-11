import asyncio, logging
from aiogram import Router, F, Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.types import LinkPreviewOptions
from server.repo import random_kata_by_day

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("random_kata"))
async def cmd_add_kata(message: Message):
    try:
        await message.answer( "Конечно, как пожелаете!" )
        res = await random_kata_by_day()
        logger.info(f"FROM BD RANDOM KATA:  {res}")
        link = res['url']
        links_text = (f'{link}')
        option_link = LinkPreviewOptions(
            url=f'{link}',
            prefer_small_media=True
        )
        name_kata = res['title'] or "Задача без названия"
        await asyncio.sleep(1.3)

        await message.answer(
            f"Вот задача! {name_kata} \n{links_text}",
            link_preview_options=option_link
        )
        await message.answer( f"Дерзай! Ты сможешь!" )
    except Exception as error:
        logger.error(f"Database operation error: {error}")
        await message.answer( "Что-то пошло не так! Ничего не нашлось!" )


