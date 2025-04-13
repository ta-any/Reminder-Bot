import asyncio, logging
from aiogram import Router, F, Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import LinkPreviewOptions
from server.repo import random_kata_by_day, stop_kata, kata_in_progress
from keyboards.for_questions import get_yon
from server.services import data_service
data_service.data = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


print("++++++++++++++++++++++++++++++++++")
logger.info('data_service: ', data_service.data)

router = Router()
count = 1

async def get_from_bd_kata(message: Message):
    if 'current_data' in data_service.data and 'current_kata_id' in data_service.data:
        del data_service.data['current_data']
        del data_service.data['current_kata_id']
        logger.info(f"clear local data_service:  {data_service.data}")
    res = await random_kata_by_day()
    logger.info(f"FROM BD RANDOM KATA:  {res}")
    data_service.data['current_data'] = res
    data_service.data['current_kata_id'] = res['id']
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
    await inline_btn(message)


async def inline_btn(message: Message):
        logger.info(f"FROM inline_btn")
        await message.answer(
            "Готовы сделать задачу?",
            reply_markup=get_yon()
        )

        @router.callback_query(F.data == "yes")
        async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
            logger.info(f"FROM inline_btn: YES!")
            logger.info(f"FROM send_random_value save RANDOM KATA:  {data_service.data['current_data']}")
            kata_ID = data_service.data['current_kata_id']
            await kata_in_progress(kata_ID)

            await callback.message.answer("Отлично! Жду твоих результатов!")
            await callback.message.answer( f"Дерзай! Ты сможешь!" )

            await callback.answer()

        @router.callback_query(F.data == "no")
        async def send_random_value(callback: types.CallbackQuery):
            global count
            logger.info(f"FROM inline_btn: NO!")
            logger.info(f"FROM count {count}")
            kata_ID = data_service.data['current_kata_id']
            await stop_kata(kata_ID)

            if count <= 3:
                await callback.message.answer("Хорошо, давай другую!")
                await get_from_bd_kata(message)
                count += 1

            else:
                await callback.message.answer("Больше нет вариантов!")

            await callback.answer()


@router.message(Command("random_kata"))
async def cmd_add_kata(message: Message):
    logger.info(' Start command "/random_kata"')
    try:
        await message.answer( "Конечно, как пожелаете!" )
        await get_from_bd_kata(message)

    except Exception as error:
        logger.error(f"Database operation error: {error}")
        await message.answer( "Что-то пошло не так! Ничего не нашлось!" )


