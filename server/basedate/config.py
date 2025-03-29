import os, psycopg2
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()
DB_CONFIG = {
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "main_table": os.getenv("DB_MAIND_TABLE"),
    "status_table": os.getenv("DB_STATUS_TABLE"),
}