import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SQL_FILE = Path(__file__).resolve().parents[1] / "database_scripts" / "001_create_chat_analytics.sql"


sql = SQL_FILE.read_text()

with psycopg.connect(DATABASE_URL) as connection:
    with connection.cursor() as cursor:
        cursor.execute(sql)

print("Migration completed.")
