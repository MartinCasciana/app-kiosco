import sqlite3
from pathlib import Path

DB_PATH = Path("kiosco.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _column_exists(conn, table: str, column: str) -> bool:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(c["name"] == column for c in cols)

def init_db():
    with get_conn() as conn:
        # Tabla base
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                cost REAL NOT NULL,
                sale REAL NOT NULL
            )
        """)

        # Migraciones suaves: agregar columnas si faltan
        if not _column_exists(conn, "products", "stock"):
            conn.execute("ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 0")

        if not _column_exists(conn, "products", "min_stock"):
            conn.execute("ALTER TABLE products ADD COLUMN min_stock INTEGER NOT NULL DEFAULT 0")

        conn.commit()
