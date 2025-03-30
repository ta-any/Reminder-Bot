import asyncio
from api.api import get_info_kata
from basedate.bd import random_kata, append_kata

async def add_kata_on_name(name_kata, languages):
    data = await get_info_kata(name_kata)
    print("FROM REPO: ", data)

    number_part = data['rank']['name'].split()[0]
    kyu = int(number_part)

    on_record = {
        'title': data['name'],
        'description': data['description'],
        'id_url': data['id'],
        'url': data['url'],
        'kyu': kyu,
        'language': languages
    }
    print("Данные для записи: ", on_record)
    append_kata(on_record)


asyncio.run(add_kata_on_name('valid-braces', 'python'))

# """ print(random_kata()) """



