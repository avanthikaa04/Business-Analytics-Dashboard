import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB = BASE_DIR / "data" / "analytics.db"
DB_PATH = Path(os.getenv("DB_PATH", str(DEFAULT_DB)))

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_no TEXT NOT NULL,
                outlet_name TEXT NOT NULL,
                order_datetime TEXT NOT NULL,
                category TEXT NOT NULL,
                order_type TEXT NOT NULL,
                item TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                settlement TEXT NOT NULL,
                brand TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_order_datetime ON order_lines(order_datetime)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bill_no ON order_lines(bill_no)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outlet ON order_lines(outlet_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON order_lines(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_order_type ON order_lines(order_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brand ON order_lines(brand)")
        conn.commit()
