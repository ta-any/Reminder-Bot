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


async def check_in_codewars(user):
    url = f"https://www.codewars.com/api/v1/users/{user}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    print("Успешный запрос!")
                    data = await response.json()
#                     user_data[user_id]['body'] = data
                    print("-------------------------------------")
#                     print(user_data[user_id]['body'])
                    print(data)
                    print("-------------------------------------")
                    return data
                else:
                    print(f"Ошибка запроса. Статус код: {response.status}")
                    return False
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return False
