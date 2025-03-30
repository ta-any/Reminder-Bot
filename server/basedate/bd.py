import psycopg2, random, asyncio, time
from psycopg2 import pool, sql, extras
from contextlib import contextmanager
from aiohttp import ClientSession

from .config import DB_CONFIG
print('DB_CONFIG', DB_CONFIG)

@contextmanager
def postgres_connection(dbname, user, password, host):
    """
    Контекстный менеджер для подключения к PostgreSQL
    Автоматически закрывает соединение при выходе из контекста
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        yield conn
    except psycopg2.DatabaseError as error:
        print(f"Database connection error: {error}")
        raise
    finally:
        if conn is not None:
            conn.close()

@contextmanager
def postgres_cursor(connection):
    """
    Контекстный менеджер для курсора PostgreSQL
    Автоматически закрывает курсор при выходе из контекста
    """
    cursor = None
    try:
        cursor = connection.cursor()
        yield cursor
    except psycopg2.DatabaseError as error:
        print(f"Cursor error: {error}")
        raise
    finally:
        if cursor is not None:
            cursor.close()

def get_random_kate(db_config, method='unprepared'):
    """
    Получает случайную запись из указанной таблицы PostgreSQL

    Параметры:
        db_config: словарь с параметрами подключения и именем таблицы
        method: 'unprepared' (для больших таблиц) или 'all' (ORDER BY RANDOM())

    Возвращает:
        Случайную запись из таблицы или None, если таблица пуста
    """

    try:
        with postgres_connection(
            dbname=db_config['name'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host']
        ) as conn:
            with postgres_cursor(conn) as cur:
                if method == 'unprepared':

                    cur.execute(sql.SQL("""
                                    SELECT * FROM {} WHERE status = 1
                                    ORDER BY RANDOM()
                                    LIMIT 1
                                """).format(sql.Identifier(db_config['main_table']))
                    )

                elif method == 'all':
                    # Простой метод с ORDER BY RANDOM()
                    cur.execute(
                        sql.SQL("SELECT COUNT(*) FROM {}").format(
                            sql.Identifier(db_config['main_table'])
                        )
                    )
                else:
                    raise ValueError("Invalid method. Use 'all' or 'unprepared'")

                return cur.fetchone()

    except psycopg2.DatabaseError as error:
        print(f"Database operation error: {error}")
        return None

def append_kata(kata):
    """
    Добавить новый кат полученный от пользователя.
    """
    print("fn append_kata()")
    db_config = DB_CONFIG
    try:
        with postgres_connection(
                dbname=db_config['name'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host']
            ) as conn:
                with postgres_cursor(conn) as cur:
                    insert_query = sql.SQL("""
                        INSERT INTO {} (title, description, id_url, url, kyu, language)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id_url) DO NOTHING
                        RETURNING id
                    """).format(
                        sql.Identifier(db_config['main_table'])
                    )

                    data = [(
                        kata['title'],
                        kata['description'],
                        kata['id_url'],
                        kata['url'],
                        kata['kyu'],
                        kata['language']
                    )]

                    # Выполняем запрос
                    extras.execute_batch(cur, insert_query, data)

                    # Явно подтверждаем изменения
                    conn.commit()

    except psycopg2.DatabaseError as error:
        print(f"Database operation error: {error}")
        return None



def change_status(id, status):
    print("ID kata: ", id)
    """
        Изменяет статус kata
    """
    print("fn change_status()")
    db_config = DB_CONFIG
    try:
        with postgres_connection(
                dbname=db_config['name'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host']
            ) as conn:
                with postgres_cursor(conn) as cur:
                    insert_query = sql.SQL("""
                        UPDATE {}
                        SET status = %s
                        WHERE id = %s
                    """).format(
                        sql.Identifier(db_config['main_table'])
                    )

                    cur.execute(insert_query, (status, id))
                    conn.commit()

    except psycopg2.DatabaseError as error:
        print(f"Database operation error: {error}")
        return None


def random_kata():
    """
    Получаем рандомный задачу из базы данных у котрой статус не готов (unprepared)
    """
    optimized_record = get_random_kate(DB_CONFIG, method='unprepared')
    print("KATA: ", optimized_record)

    return optimized_record


