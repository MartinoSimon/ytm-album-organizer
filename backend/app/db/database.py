from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

# backend/app/db/database.py  -> parents[2] = backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_conn():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"No se encontró schema.sql en: {SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_conn() as conn:
        conn.executescript(schema_sql)
        rows = conn.execute("PRAGMA table_info(albums)").fetchall()
        existing_cols = {r[1] for r in rows}
        if "browse_id" not in existing_cols:
            conn.execute("ALTER TABLE albums ADD COLUMN browse_id TEXT")
        if "cover_url" not in existing_cols:
            conn.execute("ALTER TABLE albums ADD COLUMN cover_url TEXT")