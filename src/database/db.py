import sqlite3

from src.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS scans (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    root    TEXT,
    at      TEXT,
    found   INTEGER,
    added   INTEGER,
    updated INTEGER,
    removed INTEGER
);
"""


def connect(db_path=DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
