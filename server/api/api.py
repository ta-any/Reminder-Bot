import asyncio, time
from aiohttp import ClientSession

async def get_info(name_kata):
    async with ClientSession() as session:
        url = f'https://www.codewars.com/api/v1/code-challenges/{name_kata}'

        async with session.get(url=url) as response:
            kata = await response.json()
            print("Result from api: ", kata)
            return kata



async def get_info_kata(name_kata):
    result =  await get_info(name_kata)
    print("from fn get_info_kata", result)

    return result
