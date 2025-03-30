import asyncio
from api.api import get_info_kata
from basedate.bd import random_kata

# async def add_kata_on_name(name_kata, languages):
#     data = await get_info_kata(name_kata)
#     print("FROM REPO: ", data)
#
# asyncio.run(add_kata_on_name('valid-braces', 'python'))

print(random_kata())



