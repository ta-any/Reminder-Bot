from bs4 import BeautifulSoup
from psycopg2 import pool, sql, extras
from contextlib import contextmanager
import asyncio, aiohttp

async def scrape_katas(language: str, kyu: int, page=1):
    url = f"https://www.codewars.com/kata/search/{language}?q=&r[]=-{kyu}&page={page}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                katas = []
                kata_cards = soup.find_all('div', class_='list-item-kata')

                for card in kata_cards:
                    title_link = card.find('a')
                    if title_link:
                        title = title_link.text.strip()
                        relative_url = title_link.get('href', '')
                        if relative_url:
                            kata_url = f"https://www.codewars.com{relative_url}"
                            id_url = relative_url.split('/')[-1] if relative_url.startswith('/kata/') else relative_url
                            katas.append({
                                "title": title,
                                "id_url": id_url,
                                "url": kata_url,
                                "kyu": kyu,
                                "language": language
                            })

                print(f"Найдено {len(katas)} задач")
                return katas
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []

async def scrape_katas_limit(language: str, kyu: int, count: int):
    """Получает указанное количество задач, загружая данные с нескольких страниц при необходимости"""
    katas = []
    page = 1

    if count <= 0:
        print("Количество задач должно быть положительным числом!")
        return

    while len(katas) < count:
        print(f"Загрузка страницы {page}...")
        page_katas = await scrape_katas(language, kyu, page)

        if not page_katas:  # Если задачи закончились или произошла ошибка
            break

        katas.extend(page_katas)
        page += 1

        if len(page_katas) < 30:
            break

    return katas[:count]


async def get_list_katas(language, kyu, count):
    try:

        print(f"\nЗагрузка {count} задач {kyu} kyu для языка {language}...")
        katas = await scrape_katas_limit(language, kyu, count)

        print(f"\nУспешно загружено {len(katas)} задач:")
        for i, kata in enumerate(katas, 1):
            print(f"{i}. {kata['title']} ({kata['url']})")

        return katas

    except ValueError:
        print("Ошибка ввода! Пожалуйста, вводите корректные значения.")


