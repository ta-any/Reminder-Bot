import psycopg2, random, asyncio, time, asyncpg
from psycopg2 import pool, sql, extras
from contextlib import contextmanager, asynccontextmanager
from asyncpg import Connection, Record
from typing import Optional, Dict, Any

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.info("Start get_random_kate...")
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
        logger.error(f"Database operation error: {error}")
        return None


async def append_kata(kata: Dict[str, Any]) -> Optional[int]:
    """
    Асинхронно добавляет новую кату в базу данных.
    Параметры:
        kata: Словарь с данными каты (title, description, id_url и т.д.)
    Возвращает:
        ID добавленной записи или None, если произошла ошибка или запись уже существовала
    """
    logger.info("async append_kata()")

    try:
        db_config = DB_CONFIG
        try:

            logger.info("start append_kata connect...")
            async with get_db_connection(db_config) as conn:
                logger.info("start circular: " )
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

                logger.info("finish")
                return result['id'] if result else None
        except:
            logger.error("ERROR...")

#         finally:
#             await conn.close()

    except Exception as error:
        logger.error(f"Database operation error: {error}")
        return None


async def change_status(id, status):
    """
    Асинхронно изменяет статус kata в базе данных

    Args:
        id: ID записи для обновления
        status: Новый статус
        pool: Пул соединений asyncpg
    """
    logger.info(f"fn change_status(), ID kata: {id}")

    db_config = DB_CONFIG
    try:
        logger.info("Start change_status...")
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

            logger.info("Status updated successfully")

    except psycopg2.DatabaseError as error:
        logger.error(f"Database operation error: {error}")
        return None


async def random_kata():
    """
    Получаем рандомный задачу из базы данных у котрой статус не готов (unprepared)
    """
    optimized_record = await get_random_kate(method='unprepared')
    logger.info(f"KATA: {optimized_record}")

    return optimized_record


async def create_table_if_not_exists() -> None:
    db_config = DB_CONFIG

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS codewars_katas (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            id_url VARCHAR(255) UNIQUE NOT NULL,
            url VARCHAR(255) NOT NULL,
            description TEXT,
            kyu INTEGER NOT NULL,
            language VARCHAR(50) NOT NULL,
            status INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    try:
        logger.info("Start create_table_if_not_exists...")
        async with get_db_connection(db_config) as conn:
            async with conn.transaction():
                await conn.execute(create_table_sql)
                logger.info("Таблица проверена/создана")
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы: {e}")

async def insert_katas_batch(kata_list) -> None:
    db_config = DB_CONFIG

    if not kata_list:
        logger.info("Нет данных для вставки")
        return

    try:
        logger.info("Start insert_katas_batch...")
        async with get_db_connection(db_config) as conn:
            async with conn.transaction():
                insert_query = """
                    INSERT INTO codewars_katas (title, id_url, url, kyu, language)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (id_url) DO NOTHING
                """

                data = [
                    (kata['title'], kata['id_url'], kata['url'], kata['kyu'], kata['language'])
                    for kata in kata_list
                ]

                await conn.executemany(insert_query, data)
                logger.info(f"Успешно вставлено {len(data)} записей")

                return len(data)
    except Exception as e:
        logger.error(f"Ошибка при вставке данных: {e}")

async def delay_kata(ID_kata: int) -> bool | None:
    """
    Удаляет запись из базы данных по указанному ID.

    Args:
        db_config: Конфигурация базы данных (параметры подключения)
        record_id: ID записи для удаления
        table_name: Имя таблицы, из которой нужно удалить запись

    Returns:
        bool: True если запись была удалена, False если записи с таким ID не существует
    """

    try:
        db_config = DB_CONFIG
        logger.info("Start config BD...")
        try:
            logger.info("Start get_db_connection...")
            async with get_db_connection(db_config) as conn:
                query = f"DELETE FROM  {db_config['main_table']} WHERE id = $1 RETURNING id;"
                deleted_record = await conn.fetchrow(query, ID_kata)

                return deleted_record is not None

            return None

        finally:
#             await conn.close()
            logger.info("Stop get_db_connection...")


    except Exception as error:
        logger.error(f"Database operation error: {error}")
        return None



