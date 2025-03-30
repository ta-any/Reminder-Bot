import psycopg2, random, asyncio, time, asyncpg
from psycopg2 import pool, sql, extras
from contextlib import contextmanager, asynccontextmanager
from asyncpg import Connection, Record
from typing import Optional, Dict, Any

from .config import DB_CONFIG
# print('DB_CONFIG', DB_CONFIG)


@asynccontextmanager
async def get_db_connection(db_config):
    conn = await asyncpg.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['name']
    )
    try:
        yield conn
    finally:
        await conn.close()



async def get_random_kate(method: str = 'unprepared') -> Optional[Dict[str, Any]]:
    """
    Асинхронно получает случайную запись из указанной таблицы PostgreSQL
    Параметры:
        method: 'unprepared' (для больших таблиц) или 'all' (ORDER BY RANDOM())
    Возвращает:
        Случайную запись из таблицы в виде словаря или None, если таблица пуста
    """

    try:
        db_config = DB_CONFIG
        try:
            if method == 'unprepared':
                async with get_db_connection(db_config) as conn:
                    query = f"""
                        SELECT * FROM {db_config['main_table']}
                        WHERE status = 1
                        ORDER BY RANDOM()
                        LIMIT 1
                    """
                    record: Optional[Record] = await conn.fetchrow(query)

            elif method == 'all':
                async with get_db_connection(db_config) as conn:
                    query = f"SELECT COUNT(*) FROM {db_config['main_table']}"
                    record = await conn.fetchrow(query)
            else:
                raise ValueError("Invalid method. Use 'all' or 'unprepared'")

            return dict(record) if record else None

        finally:
            await conn.close()

    except Exception as error:
        print(f"Database operation error: {error}")
        return None


async def append_kata(kata: Dict[str, Any]) -> Optional[int]:
    """
    Асинхронно добавляет новую кату в базу данных.
    Параметры:
        kata: Словарь с данными каты (title, description, id_url и т.д.)
    Возвращает:
        ID добавленной записи или None, если произошла ошибка или запись уже существовала
    """
    print("async append_kata()")

    try:
        db_config = DB_CONFIG
        try:
            async with get_db_connection(db_config) as conn:
                # Выполняем запрос на вставку
                query = f"""
                    INSERT INTO {db_config['main_table']}
                    (title, description, id_url, url, kyu, language)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (id_url) DO NOTHING

                """

                # Заметьте, что asyncpg использует $1, $2 вместо %s
                result = await conn.fetchrow(
                    query,
                    kata['title'],
                    kata['description'],
                    kata['id_url'],
                    kata['url'],
                    kata['kyu'],
                    kata['language']
                )

                print("finish")
                return result['id'] if result else None

        finally:
            await conn.close()

    except Exception as error:
        print(f"Database operation error: {error}")
        return None


async def change_status(id, status):
    """
    Асинхронно изменяет статус kata в базе данных

    Args:
        id: ID записи для обновления
        status: Новый статус
        pool: Пул соединений asyncpg
    """
    print(f"fn change_status(), ID kata: {id}")

    db_config = DB_CONFIG
    try:
        async with get_db_connection(db_config) as conn:
            async with conn.transaction():
               await conn.execute(
                    f"""
                    UPDATE {db_config['main_table']}
                    SET status = $1
                    WHERE id = $2
                    """,
                    status, id
                )

            print("Status updated successfully")

    except psycopg2.DatabaseError as error:
        print(f"Database operation error: {error}")
        return None


async def random_kata():
    """
    Получаем рандомный задачу из базы данных у котрой статус не готов (unprepared)
    """
    optimized_record = await get_random_kate(method='unprepared')
    print("KATA: ", optimized_record)

    return optimized_record


