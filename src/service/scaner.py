import logging
from pathlib import Path
import sqlite3
from datetime import datetime

from src.config import SKIP_FILES

from src.service.hasher import file_hash

logger = logging.getLogger(__name__)

def _human_size(n: int):
    size = float(n)
    for unit in ("Б", "КБ", "МБ", "ГБ", "ТБ"):
        if size < 1024:
            return f"{size} {unit}"
        size /= 1024
    return f"{size} ПБ"

def _parse_ext(ext: str):
    if not ext:
        return None

    result = set()
    for piece in ext.split(","):
        piece = piece.strip().lower()
        if piece:
            result.add(piece if piece.startswith(".") else "." + piece)

    return result or None

def walk(folder: Path, root: Path, rows: list):
    for entry in folder.iterdir():
        if entry.is_dir():
            if entry.name in SKIP_FILES:
                continue
            walk(entry, root, rows)
        elif entry.is_file():
            st = entry.stat()
            logger.debug("Нашёл файл %s, размером %s", entry.relative_to(root), st.st_size)
            rows.append(
                (
                    str(root),
                    str(entry.relative_to(root)),
                    entry.name,
                    st.st_size,
                    st.st_mtime,
                    entry.suffix
                )
            )

def index_folder(conn: sqlite3.Connection, path: str, ext: str | None=None, name: str | None=None):
    path = Path(path).resolve()
    exts = _parse_ext(ext)
    rows = []
    walk(path, path, rows)
    update = added = deleted = 0

    old = {rel: (size, mtime, hash)
         for rel, size, mtime, hash in conn.execute(
        "SELECT rel, size, mtime, hash FROM files WHERE root=?",
        (str(path),)
        ).fetchall()
    }

    selected = []
    for row in rows:
        root, rel, f_name, size, mtime, suffix = row
        if exts and suffix.lower() not in exts:
            continue
        if name and name.lower() not in f_name.lower():
            continue

        logger.info("Фалй прошел проверку на фильтры %s", rel)

        selected.append(row)

        prev = old.get(rel)
        if prev and prev[0] == size and prev[1] == mtime and prev[2] is not None:
            continue

        hash = file_hash(Path(root) / rel)

        if prev:
            conn.execute(
                """UPDATE files SET size = ?, mtime = ?, ext = ?, hash = ? WHERE root=? AND rel=?""",
                (size, mtime ,suffix, hash, root, rel),
            )
            update += 1
        else:
            conn.execute(
                """INSERT INTO files (root, rel, size, mtime, ext, hash) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (root, rel, size, mtime ,suffix, hash),
            )
            added += 1


    seen = {row[1] for row in rows}
    logger.info("old - seen: %s", old.keys() - seen)
    for rel in old.keys() - seen:
        conn.execute("DELETE FROM files WHERE root=? AND rel=?", (str(path), rel))
        deleted += 1

    return len(selected), added, update, deleted, selected

def scan(conn: sqlite3.Connection, path: str, ext: str | None=None, name: str | None=None):
    found, added, update, deleted, selected = index_folder(conn, path, ext, name)

    root = str(Path(path).resolve())

    conn.execute(
        "INSERT INTO scans (root, at, found, added, updated, removed) VALUES (?,?,?,?,?,?)",
        (root, datetime.now().isoformat(timespec="seconds"), found, added, update, deleted),
    )

    for row in selected:
        rel, size, mtime = row[1], row[3], row[4]
        print(f"Файл: {rel}, Размер файла: {_human_size(size)}, "
              f"Время изменения файла: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")

    logger.info("Готово, файлов: %s, Изменено файлов: %s, Добавленно файлов: %s, удалено: %s", len(selected), update,
                 added, deleted)

    return len(selected)