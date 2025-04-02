import asyncio, re
from asyncpg import Connection, Record
from .api.api import get_info_kata, check_in_codewars
from .basedate.bd import random_kata, append_kata, change_status, insert_katas_batch, create_table_if_not_exists
from .api.parser import get_list_katas

def transform_string(input_str):
    transformed = input_str.replace('#', 'number')
    transformed = transformed.lower()
    transformed = re.sub(r'[^a-z0-9-]', '-', transformed)
    transformed = re.sub(r'-+', '-', transformed)
    transformed = transformed.strip('-')

    return transformed


async def add_kata_on_name(name_kata, languages):
    print('start')

    try:
      data = await get_info_kata(transform_string(name_kata))
      print("FROM REPO: ", data)

      if(data.get('success')):
          return False

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
      return True

    except:
      print("An exception occurred")



# print("---------------------------------------------")
# # asyncio.run(add_kata_on_name('Scooby Doo Puzzle', 'python'))
#
# # print("---------------------------------------------")
# res = asyncio.run(random_kata())
# print("random_kata: ", res)

# res = asyncio.run(change_status(12, 3))

async def random_kata_by_day():
    print("random_kata: ")
    return await random_kata()


async def c_in_c(user):
    return await check_in_codewars(user)


async def parser_data(language, kyu, count):
    data = await get_list_katas(language, kyu, count)
    print("GET DATA FROM PARSER: ", data)

    await create_table_if_not_exists()
    await insert_katas_batch(data)


if __name__ == "__main__":
    asyncio.run(parser_data('python', 5, 100))




