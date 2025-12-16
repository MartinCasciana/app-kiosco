import sqlite3
from pathlib import Path

DB_PATH = Path("kiosco.db")

def get_conn():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                cost REAL NOT NULL,
                sale REAL NOT NULL
            )
        """)
        conn.commit()
