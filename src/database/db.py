import contextlib
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

CREATE TABLE IF NOT EXISTS files (
    root  TEXT,
    rel   TEXT,
    size  INTEGER,
    mtime REAL,
    ext   TEXT,
    hash  TEXT,
    PRIMARY KEY (root, rel)
);
"""

@contextlib.contextmanager
def connect(db_path=DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
