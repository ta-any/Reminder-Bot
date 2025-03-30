import requests, time
from bs4 import BeautifulSoup
from psycopg2 import pool, sql, extras
from contextlib import contextmanager

def scrape_katas(language: str, kyu: int, page=1):
    url = f"https://www.codewars.com/kata/search/{language}?q=&r[]=-{kyu}&page={page}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
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


# Конфигурация пула соединений
DB_CONFIG = {
    'dbname': 'breakfast',
    'user': 'postgres',
    'password': 'tinkyBelI',
    'host': 'localhost',
    'port': '5432',
    'minconn': 1,
    'maxconn': 10
}

# Инициализация пула соединений
connection_pool = None

def init_db_pool():
    global connection_pool
    try:
        connection_pool = pool.SimpleConnectionPool(
            minconn=DB_CONFIG['minconn'],
            maxconn=DB_CONFIG['maxconn'],
            **{k: v for k, v in DB_CONFIG.items() if k not in ['minconn', 'maxconn']}
        )
        print("Пул соединений успешно инициализирован")
    except Exception as e:
        print(f"Ошибка при создании пула соединений: {e}")
        raise

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    except Exception as e:
        print(f"Ошибка при получении соединения: {e}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)


def create_table_if_not_exists():
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS codewars_katas (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            id_url VARCHAR(255) UNIQUE NOT NULL,
            url VARCHAR(255) NOT NULL,
            description TEXT,
            kyu INTEGER NOT NULL,
            language VARCHAR(50) NOT NULL,
            status INTEGER DEFAULT 1,  -- Числовое значение вместо строки
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
                print("Таблица проверена/создана")
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")

def insert_katas_batch(kata_list):
    if not kata_list:
        print("Нет данных для вставки")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                insert_query = sql.SQL("""
                    INSERT INTO codewars_katas (title, id_url, url, kyu, language)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id_url) DO NOTHING
                """)

                data = [(kata['title'],
                        kata['id_url'],
                        kata['url'],
                        kata['kyu'],
                        kata['language']) for kata in kata_list]

                extras.execute_batch(cursor, insert_query, data)
                conn.commit()
                print(f"Успешно вставлено {len(data)} записей")
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")

if __name__ == "__main__":
    try:
        # Парсим данные
        python_5kyu_katas = scrape_katas("python", 3)

        # Инициализируем пул соединений
        init_db_pool()

        # Создаем таблицу если нужно
        create_table_if_not_exists()

        # Вставляем данные
        if python_5kyu_katas:
            insert_katas_batch(python_5kyu_katas)
        else:
            print("Не найдено данных для вставки")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрываем пул соединений
        if connection_pool:
            connection_pool.closeall()
            print("Пул соединений закрыт")