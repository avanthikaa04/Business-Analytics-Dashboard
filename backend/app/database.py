
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]

# Load local .env. Render will use its environment variable.
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(
        DATABASE_URL,
        connect_timeout=15,
        row_factory=dict_row
    )


def initialize_database():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_lines (
                    id BIGINT PRIMARY KEY,
                    bill_no TEXT NOT NULL,
                    outlet_name TEXT NOT NULL,
                    order_datetime TEXT NOT NULL,
                    category TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    item TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    quantity DOUBLE PRECISION NOT NULL,
                    settlement TEXT NOT NULL,
                    brand TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_order_datetime
                ON order_lines(order_datetime)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bill_no
                ON order_lines(bill_no)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_outlet
                ON order_lines(outlet_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_category
                ON order_lines(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_order_type
                ON order_lines(order_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_brand
                ON order_lines(brand)
            """)
