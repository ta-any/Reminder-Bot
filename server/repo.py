import asyncio, re
from asyncpg import Connection, Record
from api.api import get_info_kata
from basedate.bd import random_kata, append_kata, change_status

def transform_string(input_str):
    transformed = input_str.replace('#', 'number')
    transformed = transformed.lower()
    transformed = re.sub(r'[^a-z0-9-]', '-', transformed)
    transformed = re.sub(r'-+', '-', transformed)
    transformed = transformed.strip('-')

    return transformed


async def add_kata_on_name(name_kata, languages):
    data = await get_info_kata(transform_string(name_kata))
    print("FROM REPO: ", data)

    rank_name = data.get('rank', {}).get('name', '')
    print("rank_name", rank_name)
    number_part = rank_name.split()[0]
    kyu = int(number_part)

    on_record = {
        'title': data['name'],
        'description': data['description'],
        'id_url': data['id'],
        'url': data['url'],
        'kyu': kyu,
        'language': languages
    }
    print("--------------------Данные для записи-------------------------")
    print("Данные для записи: ", on_record)
    await append_kata(on_record)

print("---------------------------------------------")
# asyncio.run(add_kata_on_name('Scooby Doo Puzzle', 'python'))

# print("---------------------------------------------")
res = asyncio.run(random_kata())
print("random_kata: ", res)

# res = asyncio.run(change_status(12, 3))





